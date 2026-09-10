# Comment reprendre le travail avec votre assistant

Votre dossier documentaire, c'est **ce dossier-ci** (celui qui contient ce fichier). Toutes les sessions de travail avec votre assistant commencent ici, à la racine, jamais dans le dossier d'une seule société : il ne verrait qu'elle. Si une session s'ouvre malgré tout dans un sous-dossier, l'assistant se replace lui-même à la racine, à une exception près, signalée ci-dessous pour Codex.

## Rouvrir votre assistant au bon endroit

**Claude Code, application de bureau, onglet « Code »**
Avant d'écrire le premier message, utilisez le sélecteur de dossier de projet (« Project Folder ») au-dessus de la zone de saisie : ce dossier est dans la liste des dossiers récents, choisissez-le.

**Claude Code, terminal**
Placez-vous dans ce dossier (`cd`), puis lancez `claude`.

**Claude Cowork**
Connectez ce dossier comme dossier de travail, puis parlez normalement. Cowork n'a pas accès à la corbeille de votre ordinateur : vos suppressions arrivent dans le dossier `_corbeille/` de ce dossier, rangées par date. Rien n'est perdu, et c'est vous qui le videz.

**Codex, terminal**
Placez-vous dans ce dossier (`cd`), puis lancez `codex`. **Attention, c'est important avec Codex** : il ne lit son fichier d'instructions (`AGENTS.md`) que dans le dossier où vous ouvrez la session, sans jamais remonter aux dossiers du dessus. Ouvert ailleurs qu'ici, il ne connaîtra aucune de vos règles ni aucun de vos réglages.

**ChatGPT sur ordinateur**
Ouvrez (ou connectez) ce dossier comme dossier de travail, puis parlez normalement. S'il ne peut pas exécuter de commandes sur votre ordinateur, il vous donnera les quelques lignes à copier dans un terminal, en vous disant à chaque fois ce qu'elles font.

**Gemini CLI, terminal**
Placez-vous dans ce dossier (`cd`), puis lancez `gemini`. Il lira ses instructions dans `GEMINI.md`.

## La phrase magique

Une fois l'assistant ouvert, dites simplement :

> **Reprenons**

Il relira sa passation (`00_CONTEXTE/HANDOFF.md`), vous dira où vous en êtes, et proposera la suite. Pas besoin de retrouver l'ancienne conversation : une session neuve, ouverte ici, suffit.

## Au quotidien

- Un nouveau document (facture, contrat, courrier…) ? Déposez-le dans le dossier `a_trier/` de la structure concernée (ou de n'importe laquelle si vous hésitez), puis lancez la commande **traiter-a-trier**.
- Une question (« retrouve-moi la facture X », « combien chez ce fournisseur en 2025 ? ») ? La commande **rechercher**, suivie de votre question.
- Un doute sur l'état d'avancement ? La commande **point-etat**.

Comment on appelle une commande dépend de votre assistant :

| Assistant | Ce que vous tapez |
|---|---|
| Claude Code, Gemini CLI | `/traiter-a-trier` |
| Codex | `$traiter-a-trier` |
| Claude Cowork, ChatGPT sur ordinateur, autre | une phrase : « traite mes documents à trier » |

Le résultat est le même dans les trois cas : ces raccourcis renvoient tous à la même fiche, dans `00_CONTEXTE/commandes/`. Les autres commandes suivent la même logique : `reprendre`, `echeances`, `preparer-comptable`, `indexer`, `verifier`, `rapprocher` (si vous avez activé le module bancaire), `mettre-a-jour`.

## Deux dossiers à connaître

- `_corbeille/` : la corbeille du kit, créée dans tous les cas et utilisée quand la corbeille de votre système n'est pas accessible (machine virtuelle, disque externe, serveur sans bureau). Ce que l'assistant y met est rangé par date. Videz-le quand vous voulez : il ne le fait jamais tout seul.
- `00_CONTEXTE/SECURITE.md` : ce que fait et ne fait jamais votre assistant, où passent vos données, et les seules adresses qu'il contacte. À relire au calme.

## En cas de blocage

- Vérifiez que vous êtes connecté avec le compte qui porte votre abonnement, et redémarrez l'application : c'est banal et souvent suffisant.
- Toujours bloqué ? [Point IT offert, 30 minutes en visio](https://calendly.com/serdar-arikan-dgu-consulting/30min).
