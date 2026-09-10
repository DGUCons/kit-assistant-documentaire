"""Sortie console tolerante, partagee par les scripts du kit.

Un terminal Windows pilote a distance annonce souvent une page de codes ancienne
(cp1252) : un nom de fichier accentue ou un caractere hors de cette page faisait
alors planter le script en pleine operation. On force UTF-8 et on remplace ce qui
ne passe pas, plutot que d'interrompre le travail.

Python 3.9+, bibliotheque standard uniquement.
"""

from __future__ import annotations

import sys


def configurer() -> None:
    """A appeler en premiere ligne de main(), avant tout affichage."""
    for flux in (sys.stdout, sys.stderr):
        if hasattr(flux, "reconfigure"):
            flux.reconfigure(encoding="utf-8", errors="replace")
