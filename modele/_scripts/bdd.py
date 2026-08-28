"""Couche d'accès commune à la base index.db.

Importée par les autres scripts. Python 3.9+, bibliothèque standard uniquement.
La base vit dans 00_CONTEXTE/index.db, à côté du dossier _scripts/.
"""

from __future__ import annotations

import sqlite3
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

CHEMIN_BDD = Path(__file__).resolve().parent.parent / "index.db"


def maintenant() -> str:
    return datetime.now().isoformat(timespec="seconds")


def normaliser(chemin: str | Path) -> str:
    """Chemin absolu en texte, normalisé NFC (macOS stocke parfois les accents en NFD)."""
    return unicodedata.normalize("NFC", str(Path(chemin).resolve()))


def connexion(creer: bool = False) -> sqlite3.Connection:
    if not creer and not CHEMIN_BDD.exists():
        sys.exit(f"Base introuvable : {CHEMIN_BDD}. Lancer d'abord init_bdd.py.")
    conn = sqlite3.connect(CHEMIN_BDD)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def meta_lire(conn: sqlite3.Connection, cle: str) -> str | None:
    ligne = conn.execute("SELECT valeur FROM meta WHERE cle = ?", (cle,)).fetchone()
    return ligne["valeur"] if ligne else None


def meta_ecrire(conn: sqlite3.Connection, cle: str, valeur: str) -> None:
    conn.execute(
        "INSERT INTO meta (cle, valeur) VALUES (?, ?) "
        "ON CONFLICT(cle) DO UPDATE SET valeur = excluded.valeur",
        (cle, valeur),
    )
