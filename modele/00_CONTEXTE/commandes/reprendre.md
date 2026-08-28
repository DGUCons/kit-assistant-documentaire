# /reprendre (ou « Reprenons ») : reprendre le travail en cours

## Garde-fous

- Ne jamais reprendre une opération sans l'annoncer d'abord.
- Si le dossier courant n'est pas la racine documentaire (chemin dans les instructions permanentes), s'y replacer avant tout.

## Déroulé

1. Lire `00_CONTEXTE/HANDOFF.md`, puis croiser avec les tables `meta` et `lots` de la base (la base fait foi : elle est plus fraîche d'au plus un lot).
2. Annoncer l'état en deux phrases : où on en est, ce qu'il reste.
3. Proposer le prochain pas concret (celui du HANDOFF, corrigé par la base) et attendre l'accord.
4. Si l'installation n'est pas terminée (`meta.phase_installation` ≠ `terminee`) : reprendre le déroulé de `.kit/START.md` à la phase enregistrée, en en respectant le contrat de ton.
5. Sinon : traiter la demande du jour (dépôts en attente → proposer `/traiter-a-trier` ; décisions en attente listées au HANDOFF → les rappeler).
