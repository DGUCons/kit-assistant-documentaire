# /indexer [source] : scanner et lire ce qui est nouveau

## Garde-fous

- Incrémental par empreinte : un document déjà indexé (même empreinte SHA-256) n'est **jamais relu**.
- Si le volume à lire dépasse ~50 documents, prévenir du coût (quota) et proposer de traiter par lots, comme au premier passage.
- Jamais de dossier exclu.

## Déroulé

1. Lancer `00_CONTEXTE/_scripts/scan.py` sur la source demandée (ou `scan.py --toutes` pour toutes les sources de la table `sources`).
2. Restituer le delta : nouveaux fichiers, fichiers modifiés (empreinte changée), fichiers disparus (signalés, jamais retirés de la base : marqueur `supprime`), fichiers `non_disponible` (stubs cloud → donner la consigne « Toujours conserver sur cet appareil » et proposer un re-scan).
3. Lire les fichiers `a_lire` (par lots si nombreux) : fiche complète en base, comme en phase P3.
4. Fin de lot : journal, `HANDOFF.md`, 3 fiches d'échantillon.

## Restitution

Compteurs du delta, puis le même compte rendu qu'un lot d'indexation. Proposer `/traiter-a-trier` si les nouveautés sont dans des `a_trier/`.
