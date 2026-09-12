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
import sortie

# Dossiers de transit : un document « classé » n'a rien à y faire.
DOSSIERS_DE_TRANSIT = {"a_trier", "a_valider"}


def dans_un_dossier_de_transit(chemin: str) -> bool:
    """Comparaison sur le segment de chemin : « societe_a_trier_2024 » n'est pas
    un dossier a_trier, un LIKE '%a_trier%' le signalait à tort."""
    return any(partie in DOSSIERS_DE_TRANSIT for partie in Path(chemin).parts)


def main() -> None:
    sortie.configurer()
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

    # Un document « general » n'est rattaché à aucune structure, par décision de
    # l'utilisateur (P4) : son entite_id vide est normal, pas une fiche incomplète.
    print("--- Fiches marquées lues mais incomplètes ---")
    for ligne in conn.execute(
        "SELECT id, chemin FROM fichiers WHERE contenu_lu = 1 AND supprime = 0"
        " AND (resume IS NULL OR type_document IS NULL"
        "      OR (entite_id IS NULL AND statut_classement != 'general'))"
    ):
        anomalies += 1
        print(f"  incomplète : [{ligne['id']}] {ligne['chemin']}")

    print("--- Statuts incohérents ---")
    for ligne in conn.execute(
        "SELECT id, chemin, statut_classement, contenu_lu FROM fichiers WHERE supprime = 0"
        " AND statut_classement IN ('indexe', 'classe', 'general')"
    ):
        # Un document rangé (« classe ») ou laissé en place sans structure
        # (« general ») n'a rien à faire dans un dossier de transit.
        range_en_transit = (ligne["statut_classement"] in ("classe", "general")
                            and dans_un_dossier_de_transit(ligne["chemin"]))
        if range_en_transit or not ligne["contenu_lu"]:
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
        print(f"{anomalies} anomalie(s) : à traduire en langage simple, en un seul tableau,"
              " puis une seule question (tout corriger, ou reprendre une par une).")
        sys.exit(1)
    print("Aucune anomalie : la base et le disque sont cohérents.")


if __name__ == "__main__":
    main()
