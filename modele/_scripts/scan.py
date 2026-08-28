"""Scan incrémental d'une source documentaire.

Enregistre chaque fichier en base (empreinte SHA-256, taille, dates) SANS lire
le contenu : la lecture est le travail de l'assistant. Détecte les fichiers
« dans le nuage seulement » (OneDrive/iCloud Files On-Demand), les fichiers
modifiés, disparus, et les doublons d'empreinte.

Usage :
  python3 scan.py <chemin de la source>
  python3 scan.py --toutes            (toutes les sources non exclues de la table sources)
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import bdd

FICHIERS_IGNORES = {
    ".ds_store", "thumbs.db", "desktop.ini", "icon\r",
    # fichiers du kit posés à la racine documentaire : jamais indexés
    "claude.md", "agents.md", "gemini.md", "ouvrir_ici.md",
}
DOSSIERS_IGNORES = {".kit", ".claude", ".git", "00_CONTEXTE", "$RECYCLE.BIN", "System Volume Information"}
# les .txt jumeaux (notes explicatives) ne vivent que dans ces dossiers : ignorés
DOSSIERS_JUMEAUX = {"a_valider", "a_supprimer"}


def est_stub_cloud(chemin: Path, stat: os.stat_result) -> bool:
    """Fichier dont le contenu est resté dans le nuage : ne surtout pas le lire
    (le hachage forcerait le téléchargement de toute la source)."""
    if os.name == "nt":
        import ctypes

        FILE_ATTRIBUTE_OFFLINE = 0x1000
        FILE_ATTRIBUTE_RECALL_ON_OPEN = 0x40000
        FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS = 0x400000
        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(chemin))
        if attrs == -1:
            return False
        return bool(attrs & (FILE_ATTRIBUTE_OFFLINE | FILE_ATTRIBUTE_RECALL_ON_OPEN | FILE_ATTRIBUTE_RECALL_ON_DATA_ACCESS))
    # macOS/Linux : un fichier « dataless » annonce une taille mais n'occupe aucun bloc
    blocs = getattr(stat, "st_blocks", None)
    if blocs == 0 and stat.st_size > 0:
        if sys.platform == "darwin":
            try:
                # fichier compressé APFS (données dans un attribut étendu) : bien présent sur disque
                os.getxattr(chemin, "com.apple.decmpfs")
                return False
            except OSError:
                return True
        return True
    return False


def hacher(chemin: Path) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as flux:
        for bloc in iter(lambda: flux.read(1024 * 1024), b""):
            h.update(bloc)
    return h.hexdigest()


def est_exclu(chemin_norm: str, exclusions: list[str]) -> bool:
    """Vrai si le chemin EST une exclusion ou vit dedans. La frontière de segment
    compte : exclure « Perso » ne doit pas écarter « Perso2-boulot »."""
    return any(chemin_norm == ex or chemin_norm.startswith(ex + os.sep) for ex in exclusions)


def lister_fichiers(racine: Path, exclusions: list[str]) -> tuple[list[Path], int]:
    resultat = []
    nb_exclus = 0
    for dossier, sous_dossiers, fichiers in os.walk(racine):
        retenus = []
        for d in sous_dossiers:
            if d in DOSSIERS_IGNORES:
                continue
            if est_exclu(bdd.normaliser(Path(dossier) / d), exclusions):
                nb_exclus += 1
                continue
            retenus.append(d)
        sous_dossiers[:] = retenus
        nom_dossier = Path(dossier).name
        for nom in fichiers:
            if nom.lower() in FICHIERS_IGNORES or nom.startswith("~$"):
                continue
            if nom_dossier in DOSSIERS_JUMEAUX and nom.lower().endswith(".txt"):
                continue
            resultat.append(Path(dossier) / nom)
    return resultat, nb_exclus


def scanner_source(conn, chemin_source: str) -> None:
    source = conn.execute("SELECT * FROM sources WHERE chemin = ?", (chemin_source,)).fetchone()
    scan_partiel = False
    if source is None:
        # Sous-dossier d'une source déjà déclarée (ex. un a_trier/) : on réutilise sa
        # ligne au lieu de polluer la cartographie avec une nouvelle source.
        for ligne in conn.execute("SELECT * FROM sources WHERE exclu = 0"):
            if chemin_source == ligne["chemin"] or chemin_source.startswith(ligne["chemin"] + os.sep):
                source, scan_partiel = ligne, True
                break
    if source is None:
        racine_doc = bdd.meta_lire(conn, "racine")
        type_source = "interne" if racine_doc and (
            chemin_source == bdd.normaliser(racine_doc)
            or chemin_source.startswith(bdd.normaliser(racine_doc) + os.sep)
        ) else "local"
        with conn:
            conn.execute("INSERT INTO sources (chemin, type) VALUES (?, ?)", (chemin_source, type_source))
        source = conn.execute("SELECT * FROM sources WHERE chemin = ?", (chemin_source,)).fetchone()
    if source["exclu"]:
        print(f"Source exclue, jamais scannée : {chemin_source}")
        return

    exclusions = [ligne["chemin"] for ligne in conn.execute("SELECT chemin FROM sources WHERE exclu = 1")]
    racine = Path(chemin_source)
    if not racine.is_dir():
        sys.exit(f"Dossier introuvable : {racine}")

    quand = bdd.maintenant()
    vus: set[str] = set()
    nouveaux = modifies = stubs = inchanges = 0

    fichiers_trouves, nb_dossiers_exclus = lister_fichiers(racine, exclusions)
    for chemin in fichiers_trouves:
        cle = bdd.normaliser(chemin)
        vus.add(cle)
        stat = chemin.stat()
        existant = conn.execute("SELECT * FROM fichiers WHERE chemin = ?", (cle,)).fetchone()

        if est_stub_cloud(chemin, stat):
            stubs += 1
            with conn:
                if existant is None:
                    conn.execute(
                        "INSERT INTO fichiers (chemin, nom, extension, taille, date_modif_fichier,"
                        " date_premiere_detection, date_derniere_verification, statut_classement)"
                        " VALUES (?, ?, ?, ?, ?, ?, ?, 'non_disponible')",
                        (cle, chemin.name, chemin.suffix.lower(), stat.st_size,
                         str(int(stat.st_mtime)), quand, quand),
                    )
                else:
                    conn.execute(
                        "UPDATE fichiers SET date_derniere_verification = ?,"
                        " statut_classement = CASE WHEN contenu_lu = 1 THEN statut_classement ELSE 'non_disponible' END"
                        " WHERE id = ?",
                        (quand, existant["id"]),
                    )
            continue

        empreinte = hacher(chemin)
        with conn:
            if existant is None:
                nouveaux += 1
                conn.execute(
                    "INSERT INTO fichiers (chemin, nom, extension, hash_sha256, taille, date_modif_fichier,"
                    " date_premiere_detection, date_derniere_verification, source_id)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (cle, chemin.name, chemin.suffix.lower(), empreinte, stat.st_size,
                     str(int(stat.st_mtime)), quand, quand, source["id"]),
                )
            elif existant["hash_sha256"] != empreinte:
                modifies += 1
                conn.execute(
                    "UPDATE fichiers SET hash_sha256 = ?, taille = ?, date_modif_fichier = ?,"
                    " date_derniere_verification = ?, statut_classement = 'a_lire', contenu_lu = 0,"
                    " supprime = 0, date_suppression = NULL,"
                    " notes = COALESCE(notes || ' | ', '') || 'contenu modifié, à relire (' || ? || ')'"
                    " WHERE id = ?",
                    (empreinte, stat.st_size, str(int(stat.st_mtime)), quand, quand, existant["id"]),
                )
            else:
                inchanges += 1
                conn.execute(
                    "UPDATE fichiers SET date_derniere_verification = ?, supprime = 0, date_suppression = NULL,"
                    " statut_classement = CASE WHEN statut_classement = 'non_disponible' THEN 'a_lire'"
                    " ELSE statut_classement END WHERE id = ?",
                    (quand, existant["id"]),
                )

    # Fichiers connus sous cette source et disparus du disque : marqués, jamais effacés de la base.
    prefixe = bdd.normaliser(racine) + os.sep
    disparus = 0
    with conn:
        for ligne in conn.execute(
            "SELECT id, chemin FROM fichiers WHERE supprime = 0 AND chemin LIKE ?", (prefixe + "%",)
        ):
            if ligne["chemin"] not in vus:
                disparus += 1
                conn.execute(
                    "UPDATE fichiers SET supprime = 1, date_suppression = ? WHERE id = ?",
                    (quand, ligne["id"]),
                )
        if scan_partiel:
            # scan d'un sous-dossier : ne pas écraser le comptage global de la source
            conn.execute("UPDATE sources SET date_dernier_scan = ? WHERE id = ?", (quand, source["id"]))
        else:
            conn.execute(
                "UPDATE sources SET nb_fichiers = ?, date_dernier_scan = ?,"
                " statut = CASE WHEN statut = 'a_scanner' THEN 'scannee' ELSE statut END WHERE id = ?",
                (len(vus), quand, source["id"]),
            )

    doublons = conn.execute(
        "SELECT hash_sha256, COUNT(*) AS n FROM fichiers"
        " WHERE supprime = 0 AND hash_sha256 IS NOT NULL"
        " GROUP BY hash_sha256 HAVING n > 1"
    ).fetchall()

    a_lire = conn.execute(
        "SELECT COUNT(*) AS n FROM fichiers WHERE statut_classement = 'a_lire' AND supprime = 0"
    ).fetchone()["n"]

    print(f"Source : {racine}" + (" (scan partiel d'une source déclarée)" if scan_partiel else ""))
    print(f"  fichiers vus : {len(vus)} | nouveaux : {nouveaux} | modifiés : {modifies}"
          f" | inchangés : {inchanges} | dans le nuage seulement : {stubs} | disparus : {disparus}")
    if nb_dossiers_exclus:
        print(f"  dossiers exclus non parcourus (conformément à vos exclusions) : {nb_dossiers_exclus}")
    print(f"  empreintes en double (toutes sources confondues) : {len(doublons)}")
    print(f"  restant à lire (toutes sources confondues) : {a_lire}")
    if stubs:
        print("  → des fichiers sont restés dans le nuage : clic droit sur le dossier,"
              " « Toujours conserver sur cet appareil », puis relancer le scan.")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    conn = bdd.connexion()
    if sys.argv[1] == "--toutes":
        cibles = [ligne["chemin"] for ligne in conn.execute("SELECT chemin FROM sources WHERE exclu = 0")]
    else:
        cibles = [bdd.normaliser(sys.argv[1])]
    for cible in cibles:
        scanner_source(conn, cible)
    conn.close()


if __name__ == "__main__":
    main()
