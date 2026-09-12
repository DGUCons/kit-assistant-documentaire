# /verifier : contrôle d'intégrité base ↔ disque

## Garde-fous

- Lecture seule : le contrôle ne modifie rien. Les corrections détectées sont **proposées**, et appliquées seulement après validation.
- Un fichier disparu du disque n'est jamais retiré de la base : marqueur `supprime` + date, pour garder l'historique.

## Déroulé

1. Exécuter d'abord `00_CONTEXTE/_scripts/scan.py --toutes` (repère les fichiers présents sur disque mais inconnus de la base), puis `00_CONTEXTE/_scripts/verifier.py` : fichiers en base absents du disque, empreintes en double, fiches incomplètes, incohérences de statut (ex. `classe` mais encore dans `a_trier/`).
2. Traduire le rapport en langage simple, sans jargon.
3. Présenter les corrections **en tableau**, puis une seule question : « 1. Tout appliquer (ma recommandation) / 2. Les reprendre une par une ». N'appliquer qu'après accord (re-scan, marquage `supprime`, traitement d'un doublon selon RG.3).
4. Un document lu qui ne relève d'aucune structure ressort en « fiche incomplète » quel que soit son statut, sauf `general`. Deux cas : c'est un oubli, il faut le rattacher ou le mettre de côté ; ou c'est une note générale que l'utilisateur a décidé de garder telle quelle, et son statut doit passer à `general`, que le contrôle accepte sans rien signaler, à condition que sa fiche reste complète (type et résumé) et qu'il ne soit plus dans un dossier de transit (`a_trier/`, `a_valider/`, `a_supprimer/`).
5. Journaliser le contrôle et les corrections appliquées.

## Restitution

Verdict en une phrase (« tout est cohérent » ou « N anomalies »), puis le détail par catégorie et les corrections proposées.
