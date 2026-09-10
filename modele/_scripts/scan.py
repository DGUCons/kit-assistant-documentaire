"""Scan incrémental d'une source documentaire.

Enregistre chaque fichier en base (empreinte SHA-256, taille, dates) SANS lire
le contenu : la lecture est le travail de l'assistant. Détecte les fichiers
« dans le nuage seulement » (OneDrive/iCloud Files On-Demand), les fichiers
modifiés, disparus, et les doublons d'empreinte.

Un fichier illisible ou un dossier verrouillé n'interrompt jamais le scan : il
est compté et signalé. Les liens symboliques ne sont jamais suivis.

Usage :
  python3 scan.py <chemin de la source>
  python3 scan.py --toutes            (toutes les sources non exclues de la table sources)
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from collections import namedtuple
from pathlib import Path

import bdd
import sortie

FICHIERS_IGNORES = {
    ".ds_store", "thumbs.db", "desktop.ini", "icon\r",
    # fichiers du kit posés à la racine documentaire : jamais indexés
    "claude.md", "agents.md", "gemini.md", "ouvrir_ici.md",
}
DOSSIERS_IGNORES = {
    ".kit", ".claude", ".gemini", ".agents", ".git", "00_CONTEXTE", "_corbeille",
    "$RECYCLE.BIN", "System Volume Information",
}
# dossiers produits par /preparer-comptable : des copies, jamais des originaux
PREFIXES_DOSSIERS_IGNORES = ("transmission_",)
# les .txt jumeaux (notes explicatives) ne vivent que dans ces dossiers : ignorés
DOSSIERS_JUMEAUX = {"a_valider", "a_supprimer"}
# le kit dépose un README.md explicatif dans chacun de ces dossiers : ignoré là,
# et seulement là (un readme.md de l'utilisateur ailleurs reste un document)
DOSSIERS_README_KIT = {"a_trier", "a_valider", "a_supprimer", "archives", "_corbeille"}

# Drapeau macOS d'un fichier compressé APFS : contenu bien présent sur le disque.
UF_COMPRESSED = 0x00000020

Inventaire = namedtuple("Inventaire", "fichiers dossiers_exclus liens erreurs")


def dossier_ignore(nom: str) -> bool:
    return nom in DOSSIERS_IGNORES or nom.startswith(PREFIXES_DOSSIERS_IGNORES)


def est_readme_du_kit(chemin: Path) -> bool:
    return chemin.name.lower() == "readme.md" and chemin.parent.name in DOSSIERS_README_KIT


def est_fichier_du_kit(chemin) -> bool:
    """Fichier appartenant au kit (mode d'emploi, contexte, corbeille), jamais un document."""
    chemin = Path(chemin)
    if chemin.name.lower() in FICHIERS_IGNORES or est_readme_du_kit(chemin):
        return True
    return any(dossier_ignore(partie) for partie in chemin.parts)


def est_stub_cloud(chemin: Path, etat: os.stat_result) -> bool:
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
    blocs = getattr(etat, "st_blocks", None)
    if blocs == 0 and etat.st_size > 0:
        if sys.platform == "darwin":
            # Un fichier compressé APFS occupe lui aussi zéro bloc : le drapeau du
            # fichier le distingue (os.getxattr n'existe pas sur macOS).
            return not bool(getattr(etat, "st_flags", 0) & UF_COMPRESSED)
        return True
    return False


def hacher(chemin: Path) -> str:
    h = hashlib.sha256()
    with open(chemin, "rb") as flux:
        for bloc in iter(lambda: flux.read(1024 * 1024), b""):
            h.update(bloc)
    return h.hexdigest()


def echapper_like(texte: str) -> str:
    """Neutralise les jokers SQL « % » et « _ » d'un préfixe de chemin : sans cela,
    scanner « a_b/ » marquerait disparus les fichiers de « axb/ »."""
    for caractere in ("\\", "%", "_"):
        texte = texte.replace(caractere, "\\" + caractere)
    return texte


def est_exclu(chemin_norm: str, exclusions: list) -> bool:
    """Vrai si le chemin EST une exclusion ou vit dedans. La frontière de segment
    compte : exclure « Perso » ne doit pas écarter « Perso2-boulot »."""
    return any(chemin_norm == ex or chemin_norm.startswith(ex + os.sep) for ex in exclusions)


def lister_exclusions(conn) -> list:
    """Toutes les sources marquées exclues, normalisées (sans séparateur final)."""
    return [bdd.normaliser(ligne["chemin"])
            for ligne in conn.execute("SELECT chemin FROM sources WHERE exclu = 1")]


def lister_fichiers(racine: Path, exclusions: list) -> Inventaire:
    retenus_total = []
    dossiers_exclus = liens = erreurs = 0
    signales = []

    def signaler(erreur):
        signales.append(f"  dossier illisible, ignoré : {getattr(erreur, 'filename', erreur)}")

    for dossier, sous_dossiers, noms in os.walk(racine, onerror=signaler, followlinks=False):
        retenus = []
        for nom_sous_dossier in sous_dossiers:
            chemin_sous_dossier = Path(dossier) / nom_sous_dossier
            if dossier_ignore(nom_sous_dossier):
                continue
            if chemin_sous_dossier.is_symlink():
                liens += 1          # jamais suivi : il pourrait sortir du périmètre
                continue
            if est_exclu(bdd.normaliser(chemin_sous_dossier), exclusions):
                dossiers_exclus += 1
                continue
            retenus.append(nom_sous_dossier)
        sous_dossiers[:] = retenus

        nom_dossier = Path(dossier).name
        for nom in noms:
            if nom.lower() in FICHIERS_IGNORES or nom.startswith("~$"):
                continue
            if nom_dossier in DOSSIERS_JUMEAUX and nom.lower().endswith(".txt"):
                continue
            chemin = Path(dossier) / nom
            if est_readme_du_kit(chemin):
                continue
            if chemin.is_symlink():
                liens += 1
                continue
            retenus_total.append(chemin)

    erreurs = len(signales)
    for message in signales:
        print(message)
    return Inventaire(retenus_total, dossiers_exclus, liens, erreurs)


def trouver_source(conn, chemin_source: str):
    """Retrouve la ligne `sources` qui couvre ce chemin, en comparant des chemins
    normalisés : une source déclarée avec un séparateur final ne doit pas créer
    de doublon. Renvoie (ligne, scan_partiel) ou (None, False)."""
    partielle = None
    for ligne in conn.execute("SELECT * FROM sources"):
        declaree = bdd.normaliser(ligne["chemin"])
        if declaree == chemin_source:
            return ligne, False
        # Sous-dossier d'une source déjà déclarée (ex. un a_trier/) : on réutilise sa
        # ligne au lieu de polluer la cartographie avec une nouvelle source.
        if not ligne["exclu"] and chemin_source.startswith(declaree + os.sep):
            partielle = ligne
    return (partielle, True) if partielle is not None else (None, False)


def creer_source(conn, chemin_source: str):
    racine_doc = bdd.meta_lire(conn, "racine")
    racine_norm = bdd.normaliser(racine_doc) if racine_doc else None
    interne = racine_norm and (chemin_source == racine_norm
                               or chemin_source.startswith(racine_norm + os.sep))
    with conn:
        conn.execute("INSERT INTO sources (chemin, type) VALUES (?, ?)",
                     (chemin_source, "interne" if interne else "local"))
    return conn.execute("SELECT * FROM sources WHERE chemin = ?", (chemin_source,)).fetchone()


def scanner_source(conn, chemin_source: str) -> None:
    chemin_source = bdd.normaliser(chemin_source)

    # 1. Exclusions d'abord : rien n'est inséré en base pour un dossier exclu,
    #    ni pour un de ses sous-dossiers.
    exclusions = lister_exclusions(conn)
    if est_exclu(chemin_source, exclusions):
        print(f"Source exclue par vos réglages, jamais scannée : {chemin_source}")
        return

    # 2. Existence ensuite : pas de ligne `sources` créée pour un dossier absent.
    racine = Path(chemin_source)
    if not racine.is_dir():
        print(f"Source introuvable, ignorée : {chemin_source}")
        return

    source, scan_partiel = trouver_source(conn, chemin_source)
    if source is None:
        source = creer_source(conn, chemin_source)

    quand = bdd.maintenant()
    vus = set()
    nouveaux = modifies = stubs = inchanges = 0

    inventaire = lister_fichiers(racine, exclusions)
    illisibles = inventaire.erreurs
    for chemin in inventaire.fichiers:
        cle = bdd.normaliser(chemin)
        # Un fichier peut disparaître ou devenir illisible pendant le scan :
        # on le signale et on continue, le scan n'est jamais interrompu.
        try:
            etat = chemin.stat()
            stub = est_stub_cloud(chemin, etat)
            empreinte = None if stub else hacher(chemin)
        except OSError as erreur:
            illisibles += 1
            print(f"  fichier ignoré (illisible) : {chemin} : {erreur}")
            continue

        vus.add(cle)
        existant = conn.execute("SELECT * FROM fichiers WHERE chemin = ?", (cle,)).fetchone()

        if stub:
            stubs += 1
            with conn:
                if existant is None:
                    conn.execute(
                        "INSERT INTO fichiers (chemin, nom, extension, taille, date_modif_fichier,"
                        " date_premiere_detection, date_derniere_verification, statut_classement)"
                        " VALUES (?, ?, ?, ?, ?, ?, ?, 'non_disponible')",
                        (cle, chemin.name, chemin.suffix.lower(), etat.st_size,
                         str(int(etat.st_mtime)), quand, quand),
                    )
                else:
                    conn.execute(
                        "UPDATE fichiers SET date_derniere_verification = ?,"
                        " statut_classement = CASE WHEN contenu_lu = 1 THEN statut_classement ELSE 'non_disponible' END"
                        " WHERE id = ?",
                        (quand, existant["id"]),
                    )
            continue

        with conn:
            if existant is None:
                nouveaux += 1
                conn.execute(
                    "INSERT INTO fichiers (chemin, nom, extension, hash_sha256, taille, date_modif_fichier,"
                    " date_premiere_detection, date_derniere_verification, source_id)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (cle, chemin.name, chemin.suffix.lower(), empreinte, etat.st_size,
                     str(int(etat.st_mtime)), quand, quand, source["id"]),
                )
            elif existant["hash_sha256"] != empreinte:
                modifies += 1
                conn.execute(
                    "UPDATE fichiers SET hash_sha256 = ?, taille = ?, date_modif_fichier = ?,"
                    " date_derniere_verification = ?, statut_classement = 'a_lire', contenu_lu = 0,"
                    " supprime = 0, date_suppression = NULL,"
                    " notes = COALESCE(notes || ' | ', '') || 'contenu modifié, à relire (' || ? || ')'"
                    " WHERE id = ?",
                    (empreinte, etat.st_size, str(int(etat.st_mtime)), quand, quand, existant["id"]),
                )
            else:
                inchanges += 1
                conn.execute(
                    "UPDATE fichiers SET date_derniere_verification = ?, supprime = 0, date_suppression = NULL,"
                    " chemin_corbeille = NULL,"
                    " statut_classement = CASE WHEN statut_classement IN ('non_disponible', 'corbeille')"
                    " THEN 'a_lire' ELSE statut_classement END WHERE id = ?",
                    (quand, existant["id"]),
                )

    # Fichiers connus sous cette source et disparus du disque : marqués, jamais effacés de la base.
    prefixe = bdd.normaliser(racine) + os.sep
    disparus = 0
    with conn:
        for ligne in conn.execute(
            "SELECT id, chemin FROM fichiers WHERE supprime = 0 AND chemin LIKE ? ESCAPE '\\'",
            (echapper_like(prefixe) + "%",),
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
    print(f"  illisibles ou en erreur : {illisibles} | liens symboliques ignorés : {inventaire.liens}")
    if inventaire.dossiers_exclus:
        print(f"  dossiers exclus non parcourus (conformément à vos exclusions) : {inventaire.dossiers_exclus}")
    print(f"  empreintes en double (toutes sources confondues) : {len(doublons)}")
    print(f"  restant à lire (toutes sources confondues) : {a_lire}")
    if stubs:
        print("  des fichiers sont restés dans le nuage : clic droit sur le dossier,"
              " « Toujours conserver sur cet appareil », puis relancer le scan.")


def main() -> None:
    sortie.configurer()
    analyseur = argparse.ArgumentParser(
        description="Scan incrémental d'une source documentaire (aucun contenu n'est lu).",
        epilog="Un fichier illisible est signalé puis ignoré : le scan va toujours à son terme.",
    )
    analyseur.add_argument("chemin", nargs="?", help="dossier à scanner")
    analyseur.add_argument("--toutes", action="store_true",
                           help="scanner toutes les sources non exclues déclarées en base")
    arguments = analyseur.parse_args()
    if not arguments.toutes and not arguments.chemin:
        analyseur.error("indiquer un dossier à scanner, ou --toutes")

    conn = bdd.connexion()
    if arguments.toutes:
        cibles = [bdd.normaliser(ligne["chemin"])
                  for ligne in conn.execute("SELECT chemin FROM sources WHERE exclu = 0")]
    else:
        cibles = [bdd.normaliser(arguments.chemin)]
    for cible in cibles:
        scanner_source(conn, cible)
    conn.close()


if __name__ == "__main__":
    main()
