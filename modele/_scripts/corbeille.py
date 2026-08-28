"""Mise en corbeille RÉVERSIBLE, multi-OS. Jamais de suppression définitive.

- Windows : corbeille du système via l'API shell (SHFileOperationW, FOF_ALLOWUNDO).
- macOS  : corbeille du Finder via osascript (~/.Trash, restaurable par « Remettre »).

Usage : python3 corbeille.py <chemin> [<chemin> ...]
Sortie : une ligne par fichier, « OK » ou « ECHEC », et code retour 1 au moindre échec.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def vers_corbeille_windows(chemin: Path) -> None:
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


def vers_corbeille_macos(chemin: Path) -> None:
    script = 'tell application "Finder" to delete (POSIX file "%s" as alias)' % str(chemin).replace('"', '\\"')
    try:
        subprocess.run(["osascript", "-e", script], check=True, capture_output=True, timeout=30)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        # Repli si le Finder ne répond pas : déplacement direct vers ~/.Trash
        # (toujours réversible ; « Remettre » n'est alors pas proposé par le Finder).
        corbeille = Path.home() / ".Trash"
        destination = corbeille / chemin.name
        compteur = 1
        while destination.exists():   # jamais d'écrasement, même en corbeille
            destination = corbeille / f"{chemin.stem} ({compteur}){chemin.suffix}"
            compteur += 1
        shutil.move(str(chemin), str(destination))


def vers_corbeille(chemin: Path) -> None:
    if not chemin.exists():
        raise FileNotFoundError(chemin)
    if sys.platform == "win32":
        vers_corbeille_windows(chemin)
    elif sys.platform == "darwin":
        vers_corbeille_macos(chemin)
    else:
        sys.exit("Système non pris en charge par ce script (Windows et macOS uniquement).")
    if chemin.exists():
        raise OSError(f"Le fichier est toujours en place après l'opération : {chemin}")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    echec = False
    for argument in sys.argv[1:]:
        chemin = Path(argument).resolve()
        try:
            vers_corbeille(chemin)
            print(f"OK      {chemin}")
        except Exception as erreur:  # restitué à l'assistant, jamais silencieux
            echec = True
            print(f"ECHEC   {chemin} : {erreur}")
    sys.exit(1 if echec else 0)


if __name__ == "__main__":
    main()
