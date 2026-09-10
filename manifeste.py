"""Manifeste du kit : liste des fichiers, marque et empreinte SHA-256.

Deux usages :
  python3 manifeste.py --generer              reecrit MANIFESTE.txt depuis `git ls-files`
  python3 manifeste.py --verifier <dossier>   controle presence et empreintes d'une copie

Format d'une ligne : <marque>  <sha256>  <chemin>
  marque `kit`         : fichier remplacable par une mise a jour
  marque `utilisateur` : modele personnalise a l'installation, jamais ecrase
Une empreinte `-` signifie « presence verifiee, contenu non verifiable »
(cas de MANIFESTE.txt, qui ne peut pas contenir sa propre empreinte).

Bibliotheque standard uniquement, Python 3.9+.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from collections import namedtuple
from pathlib import Path

RACINE_PAR_DEFAUT = Path(__file__).resolve().parent
NOM_MANIFESTE = "MANIFESTE.txt"
SANS_EMPREINTE = "-"

# Fichiers dont la copie personnalisee appartient a l'utilisateur.
FICHIERS_UTILISATEUR = {"arborescence/_corbeille/README.md"}

ENTETE = """\
# MANIFESTE du kit : une ligne par fichier, <marque>  <sha256>  <chemin>
# marque `kit`         : remplacable par /mettre-a-jour
# marque `utilisateur` : modele personnalise a l'installation, JAMAIS ecrase par une mise a jour
#
# Le fichier d'instructions installe a la racine de votre dossier (CLAUDE.md, AGENTS.md
# ou GEMINI.md, selon votre assistant) est une COPIE PERSONNALISEE de modele/INSTRUCTIONS.md :
# c'est un fichier utilisateur, une mise a jour ne l'ecrase jamais.
#
# Sert au telechargement de secours (fichier par fichier) et au controle d'integrite
# (START.md, P0.7 ; commande /mettre-a-jour) : python3 manifeste.py --verifier <dossier>
# Une empreinte `-` : seule la presence du fichier est verifiee.
"""

Entree = namedtuple("Entree", "marque empreinte")


def configurer_sortie() -> None:
    """Console tolerante : un nom de fichier accentue ne doit jamais faire planter le script."""
    for flux in (sys.stdout, sys.stderr):
        if hasattr(flux, "reconfigure"):
            flux.reconfigure(encoding="utf-8", errors="replace")


def empreinte(chemin: Path) -> str:
    condensat = hashlib.sha256()
    with open(chemin, "rb") as flux:
        for bloc in iter(lambda: flux.read(1024 * 1024), b""):
            condensat.update(bloc)
    return condensat.hexdigest()


def lire(chemin_manifeste: Path) -> dict:
    """Lit un MANIFESTE. Accepte l'ancien format a deux colonnes (sans empreinte)."""
    entrees = {}
    if not chemin_manifeste.exists():
        return entrees
    for ligne in chemin_manifeste.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#"):
            continue
        morceaux = ligne.split(None, 2)
        if len(morceaux) == 3:
            marque, condensat, fichier = morceaux
        elif len(morceaux) == 2:
            marque, fichier = morceaux
            condensat = SANS_EMPREINTE
        else:
            continue
        entrees[fichier] = Entree(marque, condensat)
    return entrees


def fichiers_suivis(depot: Path) -> list:
    resultat = subprocess.run(
        ["git", "ls-files"], cwd=str(depot), capture_output=True, text=True, timeout=120,
    )
    if resultat.returncode != 0:
        sys.exit(f"`git ls-files` a echoue dans {depot} : {resultat.stderr.strip()}")
    return sorted(l for l in resultat.stdout.splitlines() if l.strip())


def marque_par_defaut(fichier: str) -> str:
    return "utilisateur" if fichier in FICHIERS_UTILISATEUR else "kit"


def generer(depot: Path) -> int:
    chemin_manifeste = depot / NOM_MANIFESTE
    anciennes = lire(chemin_manifeste)
    lignes = []
    for fichier in fichiers_suivis(depot):
        marque = anciennes[fichier].marque if fichier in anciennes else marque_par_defaut(fichier)
        condensat = SANS_EMPREINTE if fichier == NOM_MANIFESTE else empreinte(depot / fichier)
        lignes.append(f"{marque}  {condensat}  {fichier}")
    chemin_manifeste.write_text(ENTETE + "\n" + "\n".join(lignes) + "\n", encoding="utf-8")
    print(f"{len(lignes)} fichier(s) inscrits dans {chemin_manifeste}")
    return 0


EXTENSIONS_CODE = {".py", ".toml", ".json", ".sh", ".ps1", ".bat", ".cmd"}
DOSSIERS_HORS_CONTROLE = {".git", "__pycache__"}


def fichiers_de_code_en_trop(dossier: Path, entrees: dict) -> list:
    """Un fichier de code present sur le disque mais absent du manifeste est un ecart :
    un kit recupere ne doit rien contenir que le manifeste ne connaisse."""
    en_trop = []
    for chemin in sorted(dossier.rglob("*")):
        if not chemin.is_file() or chemin.suffix.lower() not in EXTENSIONS_CODE:
            continue
        relatif = chemin.relative_to(dossier)
        if DOSSIERS_HORS_CONTROLE & set(relatif.parts):
            continue
        if relatif.as_posix() not in entrees:
            en_trop.append(relatif.as_posix())
    return en_trop


def verifier(dossier: Path) -> int:
    chemin_manifeste = dossier / NOM_MANIFESTE
    entrees = lire(chemin_manifeste)
    if not entrees:
        print(f"Aucun manifeste exploitable dans {dossier} : controle impossible.")
        return 1
    ecarts = []
    for fichier, entree in sorted(entrees.items()):
        cible = dossier / fichier
        if not cible.is_file():
            ecarts.append(f"  absent      [{entree.marque}] {fichier}")
        elif entree.empreinte != SANS_EMPREINTE and empreinte(cible) != entree.empreinte:
            ecarts.append(f"  different   [{entree.marque}] {fichier}")
    for fichier in fichiers_de_code_en_trop(dossier, entrees):
        ecarts.append(f"  en trop     [?] {fichier}")
    if ecarts:
        print(f"{len(ecarts)} ecart(s) sur {len(entrees)} fichier(s) dans {dossier} :")
        print("\n".join(ecarts))
        return 1
    print(f"{len(entrees)} fichier(s) conformes au manifeste dans {dossier}.")
    return 0


def main() -> None:
    configurer_sortie()
    analyseur = argparse.ArgumentParser(
        description="Genere ou verifie le manifeste du kit (marque et empreinte SHA-256).",
    )
    groupe = analyseur.add_mutually_exclusive_group(required=True)
    groupe.add_argument("--generer", action="store_true",
                        help="reecrit MANIFESTE.txt a partir des fichiers suivis par git")
    groupe.add_argument("--verifier", metavar="DOSSIER",
                        help="controle une copie du kit contre son MANIFESTE.txt")
    analyseur.add_argument("--depot", metavar="DOSSIER", default=str(RACINE_PAR_DEFAUT),
                           help="racine du depot pour --generer (defaut : dossier de ce script)")
    arguments = analyseur.parse_args()
    if arguments.generer:
        sys.exit(generer(Path(arguments.depot).resolve()))
    sys.exit(verifier(Path(arguments.verifier).resolve()))


if __name__ == "__main__":
    main()
