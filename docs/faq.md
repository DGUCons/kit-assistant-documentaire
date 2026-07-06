# Questions fréquentes

## Pourquoi la première analyse est-elle si longue et si gourmande ?

Parce que chaque document est lu une fois, réellement. Sur des années d'archives, cela prend du temps et consomme une bonne part du quota de votre abonnement. C'est normal, prévu, et **ça n'arrive qu'une seule fois** : ensuite, seuls les nouveaux documents sont lus (quelques secondes). L'assistant vous propose d'office un traitement par lots ; si vous atteignez la limite de votre abonnement, le travail déjà fait est conservé dans l'index, vous reprenez à la session suivante.

## Quel abonnement faut-il ?

L'offre Claude Pro (environ 20 euros par mois) suffit pour un usage courant après le premier passage. Pour traiter un très gros historique plus vite, un palier supérieur accélère les choses le premier mois, puis vous pouvez redescendre.

## Ma banque n'est pas Qonto, le rapprochement bancaire marche-t-il ?

Le rapprochement décrit dans « Aller plus loin » suppose une banque qui expose une API (une interface d'interrogation pour logiciels). Qonto le fait bien ; d'autres aussi, souvent via des connecteurs. Sans API : le kit fonctionne intégralement, vous perdez juste cette extension. Et rappel non négociable : lecture seule, toujours.

## J'ai plusieurs sociétés, ou une seule, ou juste une activité indépendante ?

Le kit s'adapte : une arborescence par structure, un seul index, un seul assistant. L'entretien d'installation dimensionne tout ça.

## Mes documents sont en papier

Scannez-les d'abord (une application de scan sur téléphone suffit), déposez les PDF dans `a_trier/`. L'assistant lit très bien les scans.

## Et si j'arrête Claude un jour ?

Vous ne perdez rien : vos documents sont classés dans une arborescence claire avec des noms lisibles, et l'index est un fichier SQLite standard, lisible par des dizaines d'outils gratuits. Aucun enfermement.

## Est-ce que ça remplace mon expert-comptable ?

Non, et ce n'est pas le but. L'assistant classe, retrouve, prépare et fait un second regard. La comptabilité, les déclarations et les arbitrages restent chez votre cabinet. Il vous fera d'ailleurs gagner du temps chez eux : les pièces arrivent complètes et nommées.

## Combien de temps pour la mise en place ?

30 à 45 minutes pour l'installation guidée et le premier tri d'essai. Le traitement de l'historique dépend de son volume : comptez plusieurs sessions, par lots.

## Puis-je adapter le kit à ma sauce ?

Oui : licence MIT. Modifiez les règles, l'arborescence, la convention de nommage. Deux conseils : ne retirez jamais les règles de sécurité 1 à 3 (suppression, originaux, doublons), et notez vos adaptations dans le contexte pour que l'assistant les connaisse.

## Qui maintient ce kit ?

Serdar Arikan ([DGU Consulting](https://www.dgu-consulting.fr)), qui l'utilise en production sur ses propres sociétés. Les évolutions sont listées dans le [CHANGELOG](../CHANGELOG.md). Pour un accompagnement personnalisé : [Point IT, 30 minutes offertes](https://calendly.com/serdar-arikan-dgu-consulting/30min).
