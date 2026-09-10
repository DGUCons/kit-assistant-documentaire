# /mettre-a-jour : mettre à jour le kit installé

## Garde-fous

- **Seuls les fichiers marqués `kit` dans `.kit/MANIFESTE.txt` sont remplacés ; vos `CLAUDE.md`, `AGENTS.md` et `GEMINI.md` personnalisés ne sont jamais touchés.** Le modèle d'origine `modele/INSTRUCTIONS.md` est un fichier du kit, mais les trois copies personnalisées écrites à la racine à l'installation sont à vous : elles ne sont modifiées qu'avec votre accord, point par point.
- Ne JAMAIS toucher non plus : les fichiers personnalisés de `00_CONTEXTE/` (contexte, cartographie, règles de classement ajustées, journal, HANDOFF), la corbeille interne `_corbeille/`, vos documents, et la base `index.db` (hors migration de schéma versionnée et annoncée).
- Fichiers remplaçables : `00_CONTEXTE/_scripts/`, `00_CONTEXTE/commandes/`, `00_CONTEXTE/SECURITE.md`, `.claude/`, `.gemini/commands/`, `.agents/skills/`, et le contenu de `.kit/` (modules et documentation compris).
- Si le **modèle** d'instructions (`modele/INSTRUCTIONS.md`) a changé : présenter la différence et proposer de reporter les nouveautés dans les trois fichiers installés : fusion avec accord, jamais d'écrasement.
- Tout est journalisé ; en cas de doute, ne rien faire et le dire.

## Déroulé

1. Lire `00_CONTEXTE/VERSION_KIT` (version locale) et `https://raw.githubusercontent.com/DGUCons/kit-assistant-documentaire/main/VERSION` (version publiée). Identiques → « vous êtes à jour », terminer.
2. Récupérer le CHANGELOG publié et **raconter** ce qui a changé entre les deux versions, en langage simple. Demander si l'utilisateur veut appliquer.
3. Récupérer la nouvelle version du kit dans un emplacement temporaire, par les mêmes chemins que START.md P0.7 (kit déposé par l'utilisateur, clone, archive, fichier par fichier). Ne jamais créer de dépôt git dans le dossier documentaire : ce n'en est pas un.
4. **Vérifier l'intégrité avant de remplacer quoi que ce soit** : depuis le dossier du kit récupéré, comparer chaque fichier à son empreinte de `MANIFESTE.txt` avec l'outil du système, exactement comme START.md P0.7 (`shasum -a 256 -c` sur macOS, `sha256sum -c` sur Linux, `Get-FileHash` sur Windows) : rien de ce qui vient d'être téléchargé ne s'exécute avant vérification. Si le kit a été récupéré par `git clone`, retirer d'abord son sous-dossier `.git` avec la commande Python retenue (`import shutil; shutil.rmtree('.git')`), seule suppression définitive autorisée, comme à l'installation. Un fichier manquant ou une empreinte qui ne correspond pas : **arrêter là**, ne rien remplacer, dire lesquels, et proposer de recommencer la récupération autrement. Puis remplacer le contenu de `.kit/` et, dans le dossier documentaire, uniquement les fichiers marqués `kit` du MANIFESTE : `00_CONTEXTE/_scripts/`, `00_CONTEXTE/commandes/`, `.claude/`, `.gemini/commands/`, `.agents/skills/`, et `00_CONTEXTE/SECURITE.md` (copie de `docs/securite.md`).
5. Faire une copie de sauvegarde de la base (`index.db` copié en `index.db.avant-<version>`), puis exécuter `init_bdd.py` (idempotent) : il applique les migrations de schéma si `meta.version_schema` est en retard.
6. Si le modèle d'instructions a changé : diff présenté, fusion validée, répliquée aux trois fichiers.
7. Écrire la nouvelle version dans `00_CONTEXTE/VERSION_KIT` ET dans la clé `version_kit` de la table `meta`, journaliser, résumer ce qui a été fait.
