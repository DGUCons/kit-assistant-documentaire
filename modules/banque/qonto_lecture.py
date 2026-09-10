"""Synchronisation Qonto en LECTURE SEULE. Aucune écriture, aucun virement, jamais.

La clé d'accès vit HORS du dossier documentaire :
  ~/.config/assistant-doc/qonto.json   contient   {"login": "...", "secret_key": "..."}
(identifiants d'API Qonto : réglages de l'organisation, section « Clé API ».)

Ce script n'émet que des requêtes GET. Les transactions arrivent dans la table
`transactions` de la base ; l'identifiant Qonto (reference_externe) rend la
synchronisation rejouable sans doublon.

Usage : python3 qonto_lecture.py
"""

from __future__ import annotations

import json
import os
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

# bdd.py vit dans <racine>/00_CONTEXTE/_scripts/ ; installé, ce script vit dans
# <racine>/.kit/modules/banque/. Repli sur le dossier courant si lancé ailleurs.
_candidats = [
    Path(__file__).resolve().parents[3] / "00_CONTEXTE" / "_scripts",
    Path.cwd() / "00_CONTEXTE" / "_scripts",
]
for _c in _candidats:
    if (_c / "bdd.py").exists():
        sys.path.insert(0, str(_c))
        break
else:
    sys.exit("Impossible de trouver 00_CONTEXTE/_scripts/bdd.py : lancer ce script"
             " depuis la racine du dossier documentaire.")
import bdd  # noqa: E402
import sortie  # noqa: E402

BASE = "https://thirdparty.qonto.com/v2"
CHEMIN_CLE = Path.home() / ".config" / "assistant-doc" / "qonto.json"


def requete(chemin: str, jeton: str, parametres: dict | None = None) -> dict:
    url = f"{BASE}{chemin}"
    if parametres:
        url += "?" + urllib.parse.urlencode(parametres)
    demande = urllib.request.Request(url, method="GET", headers={
        "Authorization": jeton,
        "Accept": "application/json",
        # Cloudflare bloque l'agent par défaut de Python : agent explicite obligatoire.
        "User-Agent": "kit-assistant-documentaire (lecture seule)",
    })
    # Le jeton voyage dans l'en-tête Authorization : il n'apparaît dans aucun message.
    try:
        with urllib.request.urlopen(demande, timeout=30) as reponse:
            return json.loads(reponse.read().decode("utf-8"))
    except urllib.error.HTTPError as erreur:
        sys.exit(f"Qonto a refusé la requête {chemin} (code {erreur.code})."
                 f" Vérifiez la clé d'accès dans {CHEMIN_CLE} et ses droits en lecture.")
    except urllib.error.URLError as erreur:
        sys.exit(f"Connexion à Qonto impossible ({erreur.reason}). Vérifiez votre accès à Internet.")
    except (OSError, ValueError) as erreur:
        sys.exit(f"Réponse de Qonto inexploitable pour {chemin} : {erreur}")


def controler_droits(chemin: Path) -> None:
    """La clé d'accès bancaire ne doit être lisible que par son propriétaire."""
    if os.name == "nt":
        print(f"Avertissement : vérifiez que {chemin} n'est lisible que par votre compte Windows"
              " (Propriétés, Sécurité).")
        return
    mode = stat.S_IMODE(chemin.stat().st_mode)
    if mode & 0o077:
        sys.exit(f"Droits trop larges sur {chemin} ({oct(mode)}) : ce fichier contient une clé"
                 f" d'accès bancaire.\nCorrigez avec :  chmod 600 {chemin}")


def main() -> None:
    sortie.configurer()
    if not CHEMIN_CLE.exists():
        sys.exit(f"Clé introuvable : {CHEMIN_CLE}\nVoir modules/banque/MODULE.md pour la créer.")
    controler_droits(CHEMIN_CLE)
    identifiants = json.loads(CHEMIN_CLE.read_text(encoding="utf-8"))
    jeton = f"{identifiants['login']}:{identifiants['secret_key']}"

    conn = bdd.connexion()
    organisation = requete("/organization", jeton)["organization"]
    print(f"Organisation : {organisation.get('name', organisation['slug'])} (lecture seule)")

    total_nouvelles = 0
    for compte_api in organisation["bank_accounts"]:
        iban = compte_api.get("iban") or ""
        fin_iban = iban[-4:] if iban else ""
        compte = conn.execute(
            "SELECT id FROM comptes_bancaires WHERE actif = 1 AND iban_masque LIKE ?",
            (f"%{fin_iban}",),
        ).fetchone() if fin_iban else None
        if compte is None:
            print(f"  compte Qonto « {compte_api.get('name', '?')} » (…{fin_iban}) :"
                  " aucun compte correspondant en base (table comptes_bancaires, iban_masque)."
                  " À déclarer avant de synchroniser ce compte.")
            continue

        page, nouvelles = 1, 0
        while True:
            donnees = requete("/transactions", jeton, {
                "bank_account_id": compte_api["id"],
                "status[]": "completed",
                "per_page": 100,
                "current_page": page,
            })
            for tx in donnees["transactions"]:
                with conn:
                    curseur = conn.execute(
                        "INSERT OR IGNORE INTO transactions"
                        " (compte_id, reference_externe, date_operation, libelle, montant, sens)"
                        " VALUES (?, ?, ?, ?, ?, ?)",
                        (compte["id"], tx["transaction_id"],
                         (tx.get("settled_at") or tx.get("emitted_at") or "")[:10],
                         tx.get("label"), tx.get("amount"), tx.get("side")),
                    )
                    nouvelles += curseur.rowcount
            if donnees.get("meta", {}).get("next_page"):
                page = donnees["meta"]["next_page"]
            else:
                break
        total_nouvelles += nouvelles
        print(f"  compte …{fin_iban} : {nouvelles} nouvelle(s) transaction(s)")

    en_attente = conn.execute(
        "SELECT COUNT(*) AS n FROM transactions WHERE statut_rapprochement = 'a_rapprocher'"
    ).fetchone()["n"]
    print(f"Synchronisation terminée : {total_nouvelles} nouvelle(s), {en_attente} à rapprocher.")
    conn.close()


if __name__ == "__main__":
    main()
