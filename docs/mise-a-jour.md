# La mise à jour du kit, expliquée simplement

Votre installation garde en mémoire sa version (fichier `00_CONTEXTE/VERSION_KIT`) et une copie de référence du kit (dossier caché `.kit/` à la racine de votre dossier documentaire).

## Comment mettre à jour

Dites simplement à votre assistant, dans le dossier racine :

- Claude Code et Gemini CLI : `/mettre-a-jour`
- Codex : `$mettre-a-jour`
- Claude Cowork, ChatGPT sur ordinateur, ou tout autre : « mets le kit à jour »

Il compare votre version à la version publiée sur GitHub, **vous raconte ce qui a changé** (d'après le journal des versions), et ne fait rien sans votre accord.

Fonctionne aussi sans connexion : si vous déposez la nouvelle version du kit dans votre dossier (le fichier ZIP téléchargé depuis la page GitHub, tel quel), l'assistant la trouve et l'utilise.

## La vérification avant remplacement

Le kit publié contient un fichier `MANIFESTE.txt` qui liste chacun de ses fichiers avec son empreinte, une signature calculée sur son contenu. Avant de remplacer quoi que ce soit chez vous, l'assistant recalcule ces empreintes et les compare. Si un fichier manque ou si une empreinte ne correspond pas (téléchargement incomplet, fichier modifié en route), **il s'arrête et ne remplace rien** : il vous dit lesquels et propose de recommencer autrement.

## Ce qui est mis à jour, et ce qui ne l'est jamais

**Seuls les fichiers marqués « kit » dans `MANIFESTE.txt` sont remplacés ; vos `CLAUDE.md`, `AGENTS.md` et `GEMINI.md` personnalisés ne sont jamais touchés.**

| Mis à jour (fichiers du kit) | Jamais touché (vos fichiers) |
|---|---|
| Les scripts (`00_CONTEXTE/_scripts/`) | Vos instructions adaptées (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) |
| Les fiches de commandes (`00_CONTEXTE/commandes/`) | Votre contexte (`CONTEXTE_SOCIETES.md`, `CARTOGRAPHIE.md`) |
| Les commandes des assistants (`.claude/`, `.gemini/commands/`, `.agents/skills/`) | Vos règles de classement ajustées (`REGLES_CLASSEMENT.md`) |
| La note de sécurité (`00_CONTEXTE/SECURITE.md`) | Votre journal et votre passation (`JOURNAL_ACTIONS.md`, `HANDOFF.md`) |
| Les modules et la documentation (`.kit/`) | Votre corbeille interne (`_corbeille/`) |
| | Votre base `index.db` et, bien sûr, vos documents |

Le modèle d'instructions fait partie du kit, mais les trois fichiers personnalisés écrits chez vous à l'installation sont à vous : ils ne bougent qu'avec votre accord, différence à l'appui (voir juste en dessous).

Deux cas particuliers, toujours avec votre accord explicite :
- si le **modèle** d'instructions a évolué, l'assistant vous présente la différence et vous propose de reporter les nouveautés dans vos fichiers ;
- si le **schéma de la base** a évolué, une migration automatique est appliquée, après copie de sauvegarde de votre base (vos données sont conservées).

La liste exacte des fichiers « kit » et « utilisateur » est publique : c'est le fichier [MANIFESTE.txt](../MANIFESTE.txt) à la racine du dépôt.

## À quelle fréquence ?

Quand vous voulez. La commande `/point-etat` vous signale d'ailleurs, au passage, si une nouvelle version existe. Rien n'est jamais mis à jour automatiquement.
