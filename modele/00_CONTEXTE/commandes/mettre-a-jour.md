# /mettre-a-jour : mettre à jour le kit installé

## Garde-fous

- Ne JAMAIS toucher : les instructions adaptées (`CLAUDE.md` / `AGENTS.md` / `GEMINI.md` installés), les fichiers personnalisés de `00_CONTEXTE/` (contexte, cartographie, règles de classement ajustées, journal, HANDOFF), la base `index.db` (hors migration de schéma versionnée et annoncée).
- Seuls les fichiers marqués `kit` dans `MANIFESTE.txt` sont remplaçables (`_scripts/`, `commandes/`, `.claude/commands/`, modules, docs du `.kit/`).
- Si le **modèle** d'instructions (`modele/INSTRUCTIONS.md`) a changé : présenter la différence et proposer de reporter les nouveautés dans les trois fichiers installés : fusion avec accord, jamais d'écrasement.
- Tout est journalisé ; en cas de doute, ne rien faire et le dire.

## Déroulé

1. Lire `00_CONTEXTE/VERSION_KIT` (version locale) et `https://raw.githubusercontent.com/DGUCons/kit-assistant-documentaire/main/VERSION` (version publiée). Identiques → « vous êtes à jour », terminer.
2. Récupérer le CHANGELOG publié et **raconter** ce qui a changé entre les deux versions, en langage simple. Demander si l'utilisateur veut appliquer.
3. Mettre à jour `.kit/` en re-téléchargeant le kit (mêmes méthodes que START.md P0.7 : archive ou fichier par fichier) et en remplaçant son contenu. Ne jamais y créer de dépôt git : le dossier documentaire n'en est pas un.
4. Remplacer les fichiers marqués `kit` du MANIFESTE dans le dossier documentaire : `00_CONTEXTE/_scripts/`, `00_CONTEXTE/commandes/`, `.claude/commands/`.
5. Faire une copie de sauvegarde de la base (`index.db` copié en `index.db.avant-<version>`), puis exécuter `init_bdd.py` (idempotent) : il applique les migrations de schéma si `meta.version_schema` est en retard.
6. Si le modèle d'instructions a changé : diff présenté, fusion validée, répliquée aux trois fichiers.
7. Écrire la nouvelle version dans `00_CONTEXTE/VERSION_KIT` ET dans la clé `version_kit` de la table `meta`, journaliser, résumer ce qui a été fait.
