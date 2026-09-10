# Installation

Trois choses à faire : choisir l'assistant qui travaillera pour vous, préparer le dossier qui accueillera vos documents, et coller une phrase. Comptez 15 minutes. Aucune compétence technique n'est nécessaire, et **vous n'aurez rien d'autre à télécharger** : c'est l'assistant qui récupère le kit lui-même.

## 1. Choisir votre assistant

Le kit fonctionne avec six parcours. Le résultat sur votre disque est le même dans tous les cas : les mêmes règles, les mêmes dossiers, le même index. Prenez celui pour lequel vous avez déjà un compte.

| Parcours | Sur quel système | Ce qu'il vous faut | Comment on appelle les commandes |
|---|---|---|---|
| Claude Code en terminal | Windows, macOS, Linux | un compte Claude | `/traiter-a-trier` |
| Application Claude, onglet « Code » | Windows, macOS | un compte Claude | `/traiter-a-trier` |
| Application Claude, onglet « Cowork » | Windows, macOS | un compte Claude | une phrase : « traite mes documents à trier » |
| Codex en terminal | Windows, macOS, Linux | un compte OpenAI | `$traiter-a-trier` |
| ChatGPT sur ordinateur | Windows, macOS | un compte OpenAI | une phrase en langage courant |
| Gemini CLI en terminal | Windows, macOS, Linux | un compte Google | `/traiter-a-trier` |

Deux remarques honnêtes. Le kit a été mis au point d'abord avec Claude Code, qui reste le parcours le plus rodé, et le modèle le plus capable de votre abonnement donne de bien meilleurs résultats sur la lecture des documents (avec Claude, la commande `/model` permet d'en changer ; Opus ou supérieur est recommandé). Et un seul module, la consultation du site de votre cabinet comptable, repose sur une extension propre à Claude : partout ailleurs, il n'est pas disponible. Tout le reste fonctionne avec les six.

### Claude Code en terminal

1. Installez Claude Code en suivant la page officielle : [code.claude.com/docs](https://code.claude.com/docs).
2. Connectez-vous avec votre compte Claude.
3. Placez-vous dans le dossier prévu (`cd` vers ce dossier), puis lancez `claude`.
4. Gardez le mode de permissions par défaut : l'assistant vous demande votre accord avant chaque commande, vous validez d'une touche. La ligne du bas de la fenêtre indique le mode en cours ; si elle affiche « auto mode », appuyez sur `shift+tab` jusqu'à revenir au mode par défaut. Le mode auto décide seul et refuse les scripts du kit.

### Application Claude, onglet « Code »

1. Téléchargez l'application depuis [claude.com/claude-code](https://claude.com/claude-code), installez-la (suivant, suivant, terminer sur Windows ; glisser dans Applications sur macOS) et connectez-vous.
2. Ouvrez l'onglet « Code ».
3. **Avant d'écrire le premier message**, utilisez le sélecteur de dossier de projet (« Project Folder ») au-dessus de la zone de saisie et choisissez votre dossier. L'application le garde ensuite dans ses dossiers récents : les fois suivantes sont immédiates.
4. Gardez le mode de permissions par défaut, celui où l'assistant demande votre accord avant chaque commande : le mode auto refuse les scripts du kit.

L'application de bureau n'existe pas sur Linux : utilisez le terminal.

### Application Claude, onglet « Cowork »

1. Ouvrez l'onglet « Cowork » de l'application et connectez votre dossier de travail (c'est ce que Cowork appelle un dossier connecté).
2. Vérifiez que le dossier connecté est bien celui qui contiendra **toutes** vos sociétés, pas celui d'une seule.

Deux différences à connaître, et elles sont gérées : Cowork exécute ses commandes dans une machine séparée où votre dossier est simplement raccordé, il n'a donc pas accès à la corbeille de votre ordinateur, et sa connexion vers l'extérieur est filtrée. L'assistant s'en aperçoit tout seul au démarrage. Il utilise alors la **corbeille interne du kit** : un dossier `_corbeille/` créé à la racine de votre dossier, rangé par date, que vous voyez dans votre explorateur de fichiers et que vous videz quand vous le décidez. Rien n'est jamais supprimé pour de bon, la promesse tient. Et si le téléchargement du kit est bloqué, l'assistant vous demande simplement de déposer le fichier ZIP vous-même (voir plus bas).

### Codex en terminal

1. Installez Codex en suivant la documentation d'OpenAI et connectez-vous avec votre compte.
2. Placez-vous dans le dossier prévu (`cd`), puis lancez `codex`.

**Point important, propre à Codex** : il lit son fichier d'instructions (`AGENTS.md`) uniquement dans le dossier où vous ouvrez la session, sans jamais remonter aux dossiers du dessus. Ouvrir la session à la racine de votre dossier documentaire n'est donc pas un confort, c'est une obligation : ouverte dans le dossier d'une seule société, la session ne connaîtrait aucune de vos règles.

### ChatGPT sur ordinateur

1. Installez l'application ChatGPT pour Windows ou macOS et connectez-vous.
2. Ouvrez (ou connectez) votre dossier de travail, à la racine.

Selon la version que vous avez, l'application n'exécute pas forcément de commandes sur votre ordinateur. Ce n'est pas bloquant : l'assistant vous donne alors les quelques commandes à copier dans un terminal, une par une, en vous disant ce qu'elles font. Tout le reste (l'entretien, la lecture des documents, le classement) se passe normalement.

### Gemini CLI en terminal

1. Installez Gemini CLI en suivant la documentation de Google et connectez-vous avec votre compte.
2. Placez-vous dans le dossier prévu (`cd`), puis lancez `gemini`.

Gemini lit son fichier d'instructions (`GEMINI.md`) dans le dossier courant et dans les dossiers du dessus, et le kit lui installe ses propres commandes : `/traiter-a-trier`, `/rechercher` et les autres fonctionnent comme avec Claude Code.

## 2. Préparer le dossier racine

Créez le dossier qui contiendra **toutes vos sociétés** et la base de l'assistant, par exemple `Documents/Entreprise`. Vide, c'est le cas le plus simple. Si vous avez déjà un dossier principal qui contient un sous-dossier par société, il fait très bien l'affaire.

Ce dossier est la racine : toutes vos sessions s'ouvriront ici, jamais dans le dossier d'une seule société, sinon l'assistant ne verrait qu'elle. Il confirme ce choix avec vous pendant l'entretien, vous dit exactement ce qu'il créera, et **ne crée rien avant votre accord**.

Vous n'avez qu'une seule société et un seul dossier de documents ? L'assistant vous posera la question au démarrage et vous proposera de s'installer dans le dossier parent plutôt qu'au milieu de vos documents. Vous tranchez, il s'adapte.

## 3. La phrase à coller

Ouvrez votre assistant **dans ce dossier**, collez cette phrase et validez :

```
Récupère https://raw.githubusercontent.com/DGUCons/kit-assistant-documentaire/main/START.md et suis ces instructions pas à pas.
```

L'assistant prend le relais : il se présente, annonce ses règles, analyse votre machine et vous dit ce qu'il a trouvé, regarde le dossier où vous l'avez ouvert et vous prévient de ce qu'il y créerait, puis vous pose ses questions, une à la fois, avec sa recommandation à chaque fois. S'il vous demande l'autorisation d'accéder au réseau ou de lire des fichiers, c'est normal : accordez-la pour les étapes qu'il vous décrit.

À la session suivante, rouvrez-le au même endroit, à la racine, et dites simplement « Reprenons ». Pas besoin de retrouver l'ancienne conversation : tout est écrit dans le dossier. Le fichier `OUVRIR_ICI.md`, créé à la racine, vous le rappelle.

## Si votre connexion ne laisse pas passer le téléchargement

Cela arrive en entreprise, derrière un filtrage, ou avec un assistant dont la connexion est restreinte. Le kit s'installe quand même :

1. Depuis n'importe quel navigateur, ouvrez [la page du kit](https://github.com/DGUCons/kit-assistant-documentaire), bouton vert « Code », puis « Download ZIP ».
2. Déposez le fichier ZIP tel quel dans votre dossier racine, sans le décompresser.
3. Collez la phrase de l'étape 3 : l'assistant trouve le ZIP sur place et s'en sert.

Il vérifie ensuite que chaque fichier du kit correspond bien à son empreinte publiée avant de l'installer. Si quelque chose ne correspond pas, il s'arrête et vous le dit.

## En cas de blocage

- Vérifiez que vous êtes bien connecté avec le compte qui porte l'abonnement.
- Redémarrez l'application : c'est banal et souvent suffisant.
- Toujours bloqué ? [Réservez un Point IT](https://calendly.com/serdar-arikan-dgu-consulting/30min) (30 minutes, offert) et on le règle ensemble.
