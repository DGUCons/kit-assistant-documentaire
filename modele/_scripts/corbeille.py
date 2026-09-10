"""Mise en corbeille RÉVERSIBLE, multi-OS. Jamais de suppression définitive.

Deux corbeilles possibles :
- la corbeille du système, quand elle est utilisable (Windows, Finder sur macOS,
  `gio trash` ou le dossier freedesktop sur Linux) ;
- la corbeille interne au kit, `<racine>/_corbeille/AAAA-MM-JJ/`, visible dans
  l'explorateur de fichiers. Elle est choisie automatiquement quand la corbeille
  du système est absente (serveur, machine virtuelle, session sans bureau) ou
  quand le fichier vit sur un autre volume que la corbeille de repli Linux, cas
  où le document quitterait le disque sans que personne le voie.

Sécurité : un lien symbolique est toujours refusé (il pourrait désigner un
fichier hors de votre dossier), et seul un chemin situé sous la racine
documentaire est accepté.

Après chaque déplacement réussi, la base 00_CONTEXTE/index.db est mise à jour
(supprime = 1, statut « corbeille », date et chemin de dépôt).

Usage : python3 corbeille.py [--interne] <chemin> [<chemin> ...]
Sortie : une ligne par fichier, « OK » ou « ECHEC », et code retour 1 au moindre échec.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import bdd
import sortie

NOM_CORBEILLE_INTERNE = "_corbeille"

README_CORBEILLE = """\
# _corbeille

Ce dossier est la corbeille de l'assistant. Rien n'y est effacé : un document
déplacé ici reste entier, lisible, et peut revenir à sa place.

Il sert quand la corbeille de votre ordinateur n'est pas utilisable : ordinateur
sans bureau graphique, machine virtuelle, dossier de travail sur un disque
externe. Sinon, l'assistant utilise la corbeille habituelle de votre système.

## Comment c'est rangé

Un sous-dossier par jour, au format `AAAA-MM-JJ`. Si deux documents portent le
même nom, le second reçoit un numéro entre parenthèses : rien n'est jamais
écrasé.

## Restaurer un document

Ouvrez le sous-dossier du jour concerné et remettez le fichier où il doit être,
par un simple glisser-déposer. Vous pouvez aussi demander à l'assistant : il sait
d'où venait chaque document.

## Vider la corbeille

C'est à vous de le faire, jamais à l'assistant. Prenez le temps de regarder ce
qu'elle contient : une fois le dossier vidé, les documents sont réellement
perdus. Un bon rythme est une revue après chaque clôture comptable, quand les
comptes de l'exercice sont validés.
"""


# --------------------------------------------------------------------------
# Racine documentaire et contrôles d'entrée
# --------------------------------------------------------------------------

def racine_documentaire() -> Path:
    """La racine déclarée en base fait foi ; sinon, le dossier qui contient 00_CONTEXTE/."""
    par_defaut = None
    for dossier in Path(__file__).resolve().parents:
        if dossier.name == "00_CONTEXTE":
            par_defaut = dossier.parent
            break
    if par_defaut is None:
        par_defaut = Path(__file__).resolve().parent.parent
    if bdd.CHEMIN_BDD.exists():
        try:
            conn = sqlite3.connect(bdd.CHEMIN_BDD, timeout=30)
            conn.row_factory = sqlite3.Row
            ligne = conn.execute("SELECT valeur FROM meta WHERE cle = 'racine'").fetchone()
            conn.close()
            if ligne and ligne["valeur"] and Path(ligne["valeur"]).is_dir():
                return Path(ligne["valeur"]).resolve()
        except sqlite3.Error:
            pass   # base illisible : on retombe sur l'arborescence, jamais d'arrêt
    return par_defaut


def perimetres_autorises(racine: Path) -> list:
    """La racine documentaire, plus chaque source déclarée à l'entretien et non exclue
    (les documents vivent souvent ailleurs, dans un dossier cloud par exemple)."""
    perimetres = [bdd.normaliser(racine)]
    if bdd.CHEMIN_BDD.exists():
        try:
            conn = sqlite3.connect(bdd.CHEMIN_BDD, timeout=30)
            for (chemin,) in conn.execute("SELECT chemin FROM sources WHERE exclu = 0"):
                if chemin:
                    perimetres.append(bdd.normaliser(chemin))
            conn.close()
        except sqlite3.Error:
            pass
    return perimetres


def controler(argument: str, racine: Path) -> Path:
    """Refuse un lien symbolique et tout chemin hors de la racine documentaire
    ou des sources déclarées."""
    chemin = Path(argument).expanduser()
    if not chemin.is_absolute():
        chemin = Path.cwd() / chemin
    if chemin.is_symlink():
        raise ValueError("lien symbolique refusé : il peut désigner un fichier hors de votre dossier")
    if not chemin.exists():
        raise FileNotFoundError(f"fichier introuvable : {chemin}")
    chemin_norm = bdd.normaliser(chemin)
    if not any(chemin_norm.startswith(p + os.sep) for p in perimetres_autorises(racine)):
        raise ValueError(f"chemin hors du dossier documentaire ({racine}) et hors des sources déclarées : refusé")
    return Path(chemin_norm)


# --------------------------------------------------------------------------
# Déplacements
# --------------------------------------------------------------------------

def deplacer_sans_ecrasement(chemin: Path, dossier: Path) -> Path:
    """Déplace vers `dossier` en ajoutant un compteur si le nom est déjà pris."""
    dossier.mkdir(parents=True, exist_ok=True)
    destination = dossier / chemin.name
    compteur = 1
    while destination.exists():
        destination = dossier / f"{chemin.stem} ({compteur}){chemin.suffix}"
        compteur += 1
    shutil.move(str(chemin), str(destination))
    return destination


def vers_corbeille_interne(chemin: Path, racine: Path) -> Path:
    corbeille = racine / NOM_CORBEILLE_INTERNE
    corbeille.mkdir(parents=True, exist_ok=True)
    fiche = corbeille / "README.md"
    if not fiche.exists():
        fiche.write_text(README_CORBEILLE, encoding="utf-8")
    return deplacer_sans_ecrasement(chemin, corbeille / datetime.now().strftime("%Y-%m-%d"))


def vers_corbeille_windows(chemin: Path) -> Path:
    import ctypes
    from ctypes import wintypes

    class SHFILEOPSTRUCTW(ctypes.Structure):
        _fields_ = [
            ("hwnd", wintypes.HWND),
            ("wFunc", wintypes.UINT),
            ("pFrom", wintypes.LPCWSTR),
            ("pTo", wintypes.LPCWSTR),
            ("fFlags", ctypes.c_uint16),
            ("fAnyOperationsAborted", wintypes.BOOL),
            ("hNameMappings", ctypes.c_void_p),
            ("lpszProgressTitle", wintypes.LPCWSTR),
        ]

    FO_DELETE = 3
    FOF_ALLOWUNDO = 0x40        # passe par la corbeille : réversible
    FOF_NOCONFIRMATION = 0x10
    FOF_SILENT = 0x4

    operation = SHFILEOPSTRUCTW()
    operation.wFunc = FO_DELETE
    operation.pFrom = str(chemin) + "\0"   # liste terminée par un double NUL
    operation.fFlags = FOF_ALLOWUNDO | FOF_NOCONFIRMATION | FOF_SILENT
    resultat = ctypes.windll.shell32.SHFileOperationW(ctypes.byref(operation))
    if resultat != 0 or operation.fAnyOperationsAborted:
        raise OSError(f"SHFileOperationW a renvoyé {resultat}")
    return None   # Windows choisit lui-même l'emplacement dans sa corbeille


# Le chemin est passé en ARGUMENT à osascript, jamais collé dans le texte du
# script : un nom de fichier contenant des guillemets ne peut rien détourner.
SCRIPT_FINDER = (
    'on run argv\n'
    '  set cible to POSIX file (item 1 of argv) as alias\n'
    '  tell application "Finder" to delete cible\n'
    'end run'
)


def vers_corbeille_macos(chemin: Path) -> Path:
    corbeille = Path.home() / ".Trash"
    try:
        subprocess.run(["osascript", "-e", SCRIPT_FINDER, str(chemin)],
                       check=True, capture_output=True, timeout=30)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as erreur:
        # Repli si le Finder ne répond pas : déplacement direct vers ~/.Trash, à la
        # seule condition de rester sur le même volume (sinon le fichier quitterait
        # son disque). « Remettre » n'est alors pas proposé par le Finder.
        if volume(chemin) != volume(corbeille):
            raise OSError(f"Finder indisponible ({erreur}) et volume différent de ~/.Trash") from erreur
        return deplacer_sans_ecrasement(chemin, corbeille)
    depose = corbeille / chemin.name
    return depose if depose.exists() else corbeille


def corbeille_freedesktop() -> Path:
    """Dossier standard que lit le gestionnaire de fichiers. XDG_DATA_HOME n'est
    retenu que s'il est absolu (la spécification impose d'ignorer le reste)."""
    xdg = os.environ.get("XDG_DATA_HOME", "")
    return (Path(xdg) if os.path.isabs(xdg) else Path.home() / ".local" / "share") / "Trash"


def vers_corbeille_linux(chemin: Path) -> Path:
    # 1. L'outil GLib `gio`, présent sur la plupart des distributions : il gère lui-même
    #    la corbeille du bureau et celle des volumes externes.
    erreur_gio = ""
    if shutil.which("gio"):
        try:
            subprocess.run(["gio", "trash", str(chemin)], check=True, capture_output=True,
                           text=True, timeout=30)
            return None   # gio choisit la corbeille du volume : emplacement non garanti
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError) as erreur:
            erreur_gio = getattr(erreur, "stderr", "") or str(erreur)
    # 2. Repli : spécification freedesktop.org (Trash 1.0), même dossier que lit le bureau.
    base = corbeille_freedesktop()
    fichiers = base / "files"
    infos = base / "info"
    fichiers.mkdir(parents=True, exist_ok=True)
    infos.mkdir(parents=True, exist_ok=True)
    nom = chemin.name
    compteur = 1
    while (fichiers / nom).exists() or (infos / f"{nom}.trashinfo").exists():   # jamais d'écrasement
        nom = f"{chemin.stem} ({compteur}){chemin.suffix}"
        compteur += 1
    horodatage = datetime.now().replace(microsecond=0).isoformat()
    fiche = infos / f"{nom}.trashinfo"
    fiche.write_text(f"[Trash Info]\nPath={quote(str(chemin))}\nDeletionDate={horodatage}\n",
                     encoding="utf-8")
    try:
        shutil.move(str(chemin), str(fichiers / nom))
    except OSError as erreur:
        fiche.unlink()   # pas de fiche orpheline dans la corbeille
        detail = f" (gio avait aussi échoué : {erreur_gio.strip()})" if erreur_gio else ""
        raise OSError(f"déplacement vers la corbeille impossible : {erreur}{detail}") from erreur
    return fichiers / nom


# --------------------------------------------------------------------------
# Choix de la corbeille
# --------------------------------------------------------------------------

def volume(chemin: Path):
    """Identifiant du volume qui porte ce chemin (ou son premier parent existant)."""
    for candidat in [chemin] + list(chemin.parents):
        try:
            return candidat.stat().st_dev
        except OSError:
            continue
    return None


def disque_fixe_windows(chemin: Path) -> bool:
    """Seul un disque local fixe a une corbeille Windows : sur un partage réseau ou
    une clé USB, la suppression serait définitive malgré FOF_ALLOWUNDO."""
    import ctypes

    DRIVE_FIXED = 3
    lettre = os.path.splitdrive(str(chemin.resolve()))[0]
    if not lettre or lettre.startswith("\\\\"):
        return False
    return ctypes.windll.kernel32.GetDriveTypeW(lettre + "\\") == DRIVE_FIXED


def corbeille_systeme_disponible(chemin: Path) -> bool:
    if sys.platform == "win32":
        return disque_fixe_windows(chemin)
    if sys.platform == "darwin":
        if shutil.which("osascript") is not None:
            return True   # le Finder gère lui-même la corbeille de chaque volume
        corbeille = Path.home() / ".Trash"
        return corbeille.is_dir() and volume(chemin) == volume(corbeille)
    if sys.platform.startswith("linux"):
        if shutil.which("gio"):
            return True
        # Sans gio, le repli freedesktop copie le fichier sur le volume du dossier
        # personnel : dans une machine virtuelle, le document quitterait le disque
        # de travail. On préfère alors la corbeille interne, visible et locale.
        return volume(chemin) == volume(corbeille_freedesktop())
    return False


def deposer(chemin: Path, racine: Path, forcer_interne: bool):
    """Renvoie (libellé de la corbeille utilisée, chemin de dépôt).
    Le chemin vaut None quand c'est le système qui choisit l'emplacement."""
    if forcer_interne or not corbeille_systeme_disponible(chemin):
        return "corbeille interne du kit", vers_corbeille_interne(chemin, racine)
    try:
        if sys.platform == "win32":
            return "corbeille du système", vers_corbeille_windows(chemin)
        if sys.platform == "darwin":
            return "corbeille du système", vers_corbeille_macos(chemin)
        return "corbeille du système", vers_corbeille_linux(chemin)
    except OSError as erreur:
        # La corbeille du système a refusé : on ne renonce pas, on bascule sur la
        # corbeille interne, toujours disponible et toujours réversible.
        if chemin.exists():
            return (f"corbeille interne du kit (corbeille du système indisponible : {erreur})",
                    vers_corbeille_interne(chemin, racine))
        raise


# --------------------------------------------------------------------------
# Base de données
# --------------------------------------------------------------------------

def marquer_en_base(chemin_origine: str, chemin_corbeille) -> None:
    """Le fichier n'a pas disparu : il est en corbeille, et on note où."""
    if not bdd.CHEMIN_BDD.exists():
        return
    conn = bdd.connexion()
    try:
        with conn:
            conn.execute(
                "UPDATE fichiers SET supprime = 1, statut_classement = 'corbeille',"
                " date_suppression = ?, chemin_corbeille = ? WHERE chemin = ?",
                (bdd.maintenant(), str(chemin_corbeille) if chemin_corbeille else None,
                 chemin_origine),
            )
    except sqlite3.OperationalError as erreur:
        print(f"        base non mise à jour ({erreur}) : lancer init_bdd.py pour la migration.")
    finally:
        conn.close()


def main() -> None:
    sortie.configurer()
    analyseur = argparse.ArgumentParser(
        description="Met un ou plusieurs documents à la corbeille, de façon réversible.",
        epilog="Aucune suppression définitive n'est possible avec ce script.",
    )
    analyseur.add_argument("--interne", action="store_true",
                           help="forcer la corbeille interne au kit (<racine>/_corbeille/)")
    analyseur.add_argument("chemins", nargs="+", help="documents à mettre à la corbeille")
    arguments = analyseur.parse_args()

    racine = racine_documentaire()
    echec = False
    for argument in arguments.chemins:
        try:
            chemin = controler(argument, racine)
            origine = str(chemin)
            libelle, destination = deposer(chemin, racine, arguments.interne)
            if chemin.exists():
                raise OSError(f"le fichier est toujours en place après l'opération : {chemin}")
            ou = f" : {destination}" if destination else " (emplacement choisi par le système)"
            print(f"OK      {origine}")
            print(f"        déplacé vers la {libelle}{ou}")
            marquer_en_base(origine, destination)
        except Exception as erreur:  # restitué à l'assistant, jamais silencieux
            echec = True
            print(f"ECHEC   {argument} : {erreur}")
    sys.exit(1 if echec else 0)


if __name__ == "__main__":
    main()
