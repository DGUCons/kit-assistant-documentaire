# Questions fréquentes

## Je colle une phrase et c'est tout ? Je ne télécharge vraiment rien ?

Vraiment rien. La phrase indique à votre assistant où lire ses instructions ; il récupère lui-même le kit (des fichiers texte, publics et lisibles sur GitHub), se présente, et vous guide. Vous validez chaque étape. Le détail de ce qui est installé est dans [securite.md](securite.md), section « Ce que vous installez, exactement ».

## Pourquoi la première analyse est-elle si longue et si gourmande ?

Parce que chaque document est lu une fois, réellement. Sur des années d'archives, cela prend du temps et consomme une bonne part du quota de votre abonnement. C'est normal, prévu, et **ça n'arrive qu'une seule fois** : ensuite, seuls les nouveaux documents sont lus (quelques secondes). L'assistant traite d'office par lots.

## Une session s'arrête en plein milieu (limite d'abonnement, ordinateur fermé…) : je perds quoi ?

Rien. L'état est enregistré document par document dans la base, et un fichier de passation (`00_CONTEXTE/HANDOFF.md`) résume où vous en êtes. À la session suivante, ouvrez votre assistant dans le dossier documentaire et dites « **Reprenons** » : il reprend exactement où il s'était arrêté.

## Quel abonnement et quel modèle faut-il ?

L'offre Claude Pro (environ 20 euros par mois) suffit pour un usage courant après le premier passage. Choisissez le modèle le plus capable de votre abonnement (Opus ou supérieur recommandé ; commande `/model`). Pour traiter un très gros historique plus vite, un palier supérieur accélère le premier mois, puis vous pouvez redescendre.

## Ça marche avec un autre assistant que Claude (Codex, Gemini) ?

En principe oui : la même phrase de démarrage fonctionne, et le kit s'adapte (chaque assistant lit son propre fichier d'instructions). Mais soyons honnêtes : le kit n'a été **testé qu'avec Claude Code**, et un module (la consultation du site de votre cabinet via le navigateur) est propre à Claude. L'assistant vous le dira lui-même au démarrage. Retours bienvenus.

## Ma banque n'est pas Qonto, le rapprochement bancaire marche-t-il ?

Le module bancaire suppose une banque qui expose une API (une interface d'interrogation pour logiciels). Qonto le fait bien ; d'autres aussi. Sans API : le kit fonctionne intégralement, vous perdez juste ce module. Et rappel non négociable : lecture seule, toujours.

## J'ai plusieurs sociétés, ou une seule, ou juste une activité indépendante ?

Le kit s'adapte : une arborescence par structure, un seul index, un seul assistant. L'entretien d'installation dimensionne tout, et l'assistant peut même retrouver les informations officielles de vos structures (SIREN, forme, activité) sur l'annuaire public des entreprises, avec votre validation à chaque fois.

## Mes documents sont éparpillés (ordinateur, OneDrive, Google Drive, mails, papier)

C'est prévu : l'entretien cartographie tous ces endroits, lieu par lieu, et l'indexation les couvre tous. Les mails ne sont pas lus : exportez les pièces jointes importantes en PDF dans le dossier de dépôt. Le papier se scanne (une application de téléphone suffit).

## Comment le kit se met-il à jour ?

Dites `/mettre-a-jour` : l'assistant compare votre version à la version publiée, vous raconte ce qui a changé, et ne remplace que les fichiers du kit, jamais vos instructions adaptées, votre contexte ni votre base. Détail dans [mise-a-jour.md](mise-a-jour.md).

## Et si j'arrête Claude un jour ?

Vous ne perdez rien : vos documents sont classés dans une arborescence claire avec des noms lisibles, et l'index est un fichier SQLite standard, lisible par des dizaines d'outils gratuits. Aucun enfermement.

## Est-ce que ça remplace mon expert-comptable ?

Non, et ce n'est pas le but. L'assistant classe, retrouve, prépare et fait un second regard. La comptabilité, les déclarations et les arbitrages restent chez votre cabinet. Il vous fera d'ailleurs gagner du temps chez eux : les pièces arrivent complètes et nommées.

## Combien de temps pour la mise en place ?

Comptez une bonne heure pour l'entretien, l'installation et le premier tri d'essai supervisé. Le traitement de l'historique dépend de son volume : comptez plusieurs sessions, par lots ; l'assistant vous donne une estimation dès la cartographie.

## Puis-je adapter le kit à ma sauce ?

Oui : licence MIT. Modifiez les règles, l'arborescence, la convention de nommage. Deux conseils : ne retirez jamais les règles de sécurité (suppression, originaux, doublons), et notez vos adaptations dans le contexte pour que l'assistant les connaisse.

## Qui maintient ce kit ?

Serdar Arikan ([DGU Consulting](https://www.dgu-consulting.fr)), qui l'utilise en production sur ses propres sociétés. Les évolutions sont listées dans le [CHANGELOG](../CHANGELOG.md). Pour un accompagnement personnalisé : [Point IT, 30 minutes offertes](https://calendly.com/serdar-arikan-dgu-consulting/30min).
