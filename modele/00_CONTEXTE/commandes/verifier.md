# /verifier : contrôle d'intégrité base ↔ disque

## Garde-fous

- Lecture seule : le contrôle ne modifie rien. Les corrections détectées sont **proposées**, et appliquées seulement après validation.
- Un fichier disparu du disque n'est jamais retiré de la base : marqueur `supprime` + date, pour garder l'historique.

## Déroulé

1. Exécuter d'abord `00_CONTEXTE/_scripts/scan.py --toutes` (repère les fichiers présents sur disque mais inconnus de la base), puis `00_CONTEXTE/_scripts/verifier.py` : fichiers en base absents du disque, empreintes en double, fiches incomplètes, incohérences de statut (ex. `classe` mais encore dans `a_trier/`).
2. Traduire le rapport en langage simple, sans jargon.
3. Proposer les corrections une par une (re-scan, marquage `supprime`, traitement d'un doublon selon RG.3) et n'appliquer qu'après accord.
4. Journaliser le contrôle et les corrections appliquées.

## Restitution

Verdict en une phrase (« tout est cohérent » ou « N anomalies »), puis le détail par catégorie et les corrections proposées.
