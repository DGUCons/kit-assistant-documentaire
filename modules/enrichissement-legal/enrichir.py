"""Recherche des informations légales publiques d'une entreprise française.

Interroge l'API publique et gratuite de l'annuaire des entreprises
(recherche-entreprises.api.gouv.fr, sans clé d'accès). Lecture seule.

Le script AFFICHE les fiches candidates ; il n'écrit rien en base : la
validation humaine (anti-homonymes) et l'enregistrement sont le travail de
l'assistant, après accord de l'utilisateur.

Usage : python3 enrichir.py "nom de l'entreprise"
"""

from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request

API = "https://recherche-entreprises.api.gouv.fr/search"

# Codes INSEE de nature juridique les plus courants (libellé indicatif ;
# code inconnu → affiché brut avec la mention « code INSEE »).
FORMES = {
    "1000": "Entrepreneur individuel",
    "5202": "Société en nom collectif",
    "5306": "Société civile de moyens",
    "5410": "SARL unipersonnelle (EURL)",
    "5498": "SARL unipersonnelle (EURL)",
    "5499": "SARL",
    "5505": "SA à conseil d'administration",
    "5710": "SAS",
    "5720": "SASU",
    "6220": "GIE",
    "6521": "SCPI",
    "6540": "SCI",
    "6599": "Société civile",
    "9220": "Association déclarée",
}


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    nom = " ".join(sys.argv[1:])
    url = API + "?" + urllib.parse.urlencode({"q": nom, "per_page": 5, "page": 1})
    with urllib.request.urlopen(url, timeout=30) as reponse:
        donnees = json.loads(reponse.read().decode("utf-8"))

    resultats = donnees.get("results", [])
    if not resultats:
        print(f"Aucun résultat pour « {nom} ». Demander les informations à la main (« à vérifier » accepté).")
        return

    print(f"{len(resultats)} fiche(s) candidate(s) pour « {nom} », à faire valider par l'utilisateur :\n")
    for i, r in enumerate(resultats, 1):
        siege = r.get("siege") or {}
        dirigeants = ", ".join(
            " ".join(filter(None, [d.get("prenoms"), d.get("nom"), d.get("denomination")]))
            for d in (r.get("dirigeants") or [])[:3]
        ) or "non publié"
        code_forme = str(r.get("nature_juridique", "?"))
        forme = FORMES.get(code_forme, f"code INSEE {code_forme}")
        print(f"[{i}] {r.get('nom_complet', '?')}")
        print(f"    SIREN : {r.get('siren', '?')} | forme : {forme}"
              f" | APE : {r.get('activite_principale', '?')}")
        etat = {"A": "active", "C": "cessée"}.get(r.get("etat_administratif", ""), r.get("etat_administratif", "?"))
        print(f"    siège : {siege.get('code_postal', '')} {siege.get('libelle_commune', '?')}"
              f" | créée le : {r.get('date_creation', '?')} | société {etat}")
        print(f"    dirigeant(s) : {dirigeants}\n")

    print("Rappel : présenter la fiche (nom, SIREN, ville, dirigeant) et obtenir la validation"
          " de l'utilisateur AVANT tout enregistrement. Ne jamais deviner entre deux homonymes.")


if __name__ == "__main__":
    main()
