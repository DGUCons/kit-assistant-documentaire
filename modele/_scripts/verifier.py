"""Contrôle d'intégrité entre la base et le disque. Lecture seule : ne modifie rien.

Vérifie : fichiers en base absents du disque, incohérences de statut,
empreintes en double, fiches incomplètes, cohérence des compteurs.

Usage : python3 verifier.py
Code retour : 0 si tout est cohérent, 1 sinon.
"""

from __future__ import annotations

import sys
from pathlib import Path

import bdd


def main() -> None:
    conn = bdd.connexion()
    anomalies = 0

    print("--- Fichiers en base absents du disque (hors corbeille et déjà marqués) ---")
    for ligne in conn.execute(
        "SELECT id, chemin FROM fichiers WHERE supprime = 0 AND statut_classement != 'corbeille'"
    ):
        if not Path(ligne["chemin"]).exists():
            anomalies += 1
            print(f"  absent : [{ligne['id']}] {ligne['chemin']}")

    # Les doublons sont des constats, pas des anomalies : pendant l'indexation (P3)
    # ils sont attendus et seulement notés ; ils se traitent en P5 selon RG.3.
    doublons = 0
    print("--- Empreintes en double (constat, à traiter selon RG.3, hors code retour) ---")
    for ligne in conn.execute(
        "SELECT hash_sha256, COUNT(*) AS n, GROUP_CONCAT(chemin, ' || ') AS chemins"
        " FROM fichiers WHERE supprime = 0 AND hash_sha256 IS NOT NULL"
        " GROUP BY hash_sha256 HAVING n > 1"
    ):
        doublons += 1
        print(f"  {ligne['n']} exemplaires : {ligne['chemins']}")

    print("--- Fiches marquées lues mais incomplètes ---")
    for ligne in conn.execute(
        "SELECT id, chemin FROM fichiers WHERE contenu_lu = 1 AND supprime = 0"
        " AND (resume IS NULL OR type_document IS NULL OR entite_id IS NULL)"
    ):
        anomalies += 1
        print(f"  incomplète : [{ligne['id']}] {ligne['chemin']}")

    print("--- Statuts incohérents ---")
    for ligne in conn.execute(
        "SELECT id, chemin, statut_classement FROM fichiers WHERE supprime = 0 AND ("
        " (statut_classement = 'classe' AND (chemin LIKE '%a_trier%' OR chemin LIKE '%a_valider%'))"
        " OR (statut_classement IN ('indexe','classe') AND contenu_lu = 0))"
    ):
        anomalies += 1
        print(f"  [{ligne['id']}] {ligne['statut_classement']} : {ligne['chemin']}")

    compteurs = conn.execute(
        "SELECT statut_classement, COUNT(*) AS n FROM fichiers WHERE supprime = 0"
        " GROUP BY statut_classement ORDER BY n DESC"
    ).fetchall()
    total = sum(ligne["n"] for ligne in compteurs)
    print(f"--- Compteurs ({total} fichiers actifs) ---")
    for ligne in compteurs:
        print(f"  {ligne['statut_classement']} : {ligne['n']}")

    conn.close()
    if doublons:
        print(f"\n{doublons} groupe(s) de doublons d'empreinte (attendu pendant l'indexation, à traiter en P5).")
    if anomalies:
        print(f"{anomalies} anomalie(s) : à traduire en langage simple et à proposer une par une.")
        sys.exit(1)
    print("Aucune anomalie : la base et le disque sont cohérents.")


if __name__ == "__main__":
    main()
