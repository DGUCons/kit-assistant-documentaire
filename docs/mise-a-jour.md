# La mise à jour du kit, expliquée simplement

Votre installation garde en mémoire sa version (fichier `00_CONTEXTE/VERSION_KIT`) et une copie de référence du kit (dossier caché `.kit/` à la racine de votre dossier documentaire).

## Comment mettre à jour

Dites simplement à votre assistant :

```
/mettre-a-jour
```

Il compare votre version à la version publiée sur GitHub, **vous raconte ce qui a changé** (d'après le journal des versions), et ne fait rien sans votre accord.

## Ce qui est mis à jour, et ce qui ne l'est jamais

| Mis à jour (fichiers du kit) | Jamais touché (vos fichiers) |
|---|---|
| Les scripts (`00_CONTEXTE/_scripts/`) | Vos instructions adaptées (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) |
| Les fiches de commandes (`00_CONTEXTE/commandes/`, `.claude/commands/`) | Votre contexte (`CONTEXTE_SOCIETES.md`, `CARTOGRAPHIE.md`) |
| Les modules et la documentation (`.kit/`) | Vos règles de classement ajustées (`REGLES_CLASSEMENT.md`) |
| | Votre journal et votre passation (`JOURNAL_ACTIONS.md`, `HANDOFF.md`) |
| | Votre base `index.db` et, bien sûr, vos documents |

Deux cas particuliers, toujours avec votre accord explicite :
- si le **modèle** d'instructions a évolué, l'assistant vous présente la différence et vous propose de reporter les nouveautés dans vos fichiers ;
- si le **schéma de la base** a évolué, une migration automatique est appliquée, après copie de sauvegarde de votre base (vos données sont conservées).

La liste exacte des fichiers « kit » et « utilisateur » est publique : c'est le fichier [MANIFESTE.txt](../MANIFESTE.txt) à la racine du dépôt.

## À quelle fréquence ?

Quand vous voulez. La commande `/point-etat` vous signale d'ailleurs, au passage, si une nouvelle version existe. Rien n'est jamais mis à jour automatiquement.
