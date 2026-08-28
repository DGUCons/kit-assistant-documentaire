# Kit assistant documentaire IA

Confiez le classement des documents de votre entreprise à un assistant IA, sans jamais perdre le contrôle.

Un assistant qui mène l'entretien, cartographie vos documents où qu'ils soient, lit et indexe tout votre historique, vous pose les bonnes questions, puis vous propose un rangement que vous validez. Utilisé en production sur trois sociétés réelles : plus de 3 100 documents indexés, zéro doublon résiduel, zéro document fantôme.

## Installer : une seule phrase à coller

1. Installez [Claude Code](https://claude.com/claude-code) et connectez-vous avec votre compte Claude (le pas à pas illustré est dans [INSTALLATION.md](INSTALLATION.md)).
2. Ouvrez Claude Code et collez ceci :

```
Récupère https://raw.githubusercontent.com/DGUCons/kit-assistant-documentaire/main/START.md et suis ces instructions pas à pas.
```

C'est tout. **Vous ne téléchargez rien vous-même** : l'assistant récupère le kit, se présente, annonce ses règles, puis mène l'entretien sur vos sociétés (il peut retrouver lui-même leurs informations officielles sur l'annuaire public des entreprises), votre banque, votre cabinet comptable, et tous les endroits où vivent vos documents aujourd'hui. À chaque question, il donne sa recommandation ; à chaque étape, il attend votre accord.

## Ce qui se passe ensuite

![Schéma : chaque document lu une fois, puis indexé en base locale](docs/captures/architecture.png)

1. **L'entretien** (15 à 20 minutes) : structures, comptabilité, banques, cartographie complète de vos documents, dossiers à ne jamais lire.
2. **L'installation** (10 minutes) : votre dossier documentaire unique, ses règles, sa base d'indexation locale, et des commandes prêtes à l'emploi (`/traiter-a-trier`, `/rechercher`, `/point-etat`…).
3. **L'indexation** (plusieurs sessions) : chaque document est lu **une seule fois**, réellement, puis fiché dans une petite base locale (empreinte, date, type, émetteur, montants, résumé). Une session s'interrompt ? Rien n'est perdu, la suivante reprend exactement où vous en étiez : dites juste « Reprenons ».
4. **Les questions** : ce que les documents n'ont pas révélé, l'assistant vous le demande, jamais l'inverse.
5. **Le rangement** : une arborescence propre, proposée d'après votre corpus réel, validée avec vous, appliquée par petits plans réversibles.

Ensuite, au quotidien : vous déposez, il classe, vous tranchez les cas douteux, le journal garde trace de tout. Vos recherches interrogent l'index et répondent en quelques secondes.

## Les garde-fous

L'assistant travaille sous des règles non négociables, détaillées dans [docs/securite.md](docs/securite.md) :

- il ne supprime jamais rien définitivement : tout passe par la corbeille, réversible
- il ne modifie et n'écrase jamais un document original
- il journalise chaque action, datée, dans un fichier que vous pouvez relire
- un doublon n'est déclaré doublon que preuve à l'appui (empreinte SHA-256), jamais sur la foi du nom
- il lit le contenu réel de chaque document avant de le classer
- il n'invente jamais une information absente des documents
- les systèmes externes (banque comprise) sont en lecture seule absolue : jamais d'écriture, jamais de virement
- il ne remplace ni votre expert-comptable, ni votre avocat

Et avant de commencer, il audite même vos réglages d'assistant existants pour vous signaler toute consigne qui entrerait en conflit avec ces règles.

## Ce que vous installez, exactement

Uniquement des fichiers texte lisibles : des instructions en français et quelques petits scripts Python que vous pouvez ouvrir et lire. **Zéro exécutable, zéro installateur, zéro composant caché.** Tout est public et inspectable sur cette page avant la moindre installation. Vos documents restent chez vous ; il n'existe aucun serveur du kit. Licence [MIT](LICENSE) : utilisez, adaptez, partagez librement.

## Compatibilité

Conçu, optimisé et **testé avec Claude Code** (modèle Opus ou supérieur recommandé). Il fonctionne en principe avec d'autres assistants en ligne de commande (OpenAI Codex, Google Gemini CLI) : le kit s'adapte et le signale honnêtement, mais ces parcours n'ont pas été testés (retours bienvenus). Windows et macOS.

## Le coût, honnêtement

- L'abonnement Claude Pro (environ 20 euros par mois) suffit pour un usage courant. Pour traiter un gros historique plus vite au démarrage, un palier supérieur accélère le premier mois, puis vous pouvez redescendre.
- **Le premier passage sur votre historique est le moment coûteux** : chaque document est lu une fois. C'est long, cela consomme une bonne part du quota de votre abonnement, c'est normal, et cela n'arrive qu'une seule fois. L'assistant traite par lots, sur plusieurs sessions ; si vous atteignez la limite, le travail est conservé, vous reprenez plus tard.
- Ensuite, seuls les nouveaux documents sont lus : quelques secondes, coût marginal.

## Aller plus loin

Trois modules optionnels, proposés au bon moment et jamais imposés :

- **Rapprochement bancaire** : si votre banque expose une API (Qonto, par exemple), chaque facture est reliée à son paiement, en lecture seule, jamais d'écriture, jamais de virement.
- **Cabinet en ligne** : consultez avec l'assistant l'interface de votre cabinet (Dougs, Indy, Pennylane…) en lecture, pour repérer les pièces manquantes (Claude Code uniquement).
- **Échéancier** : les dates limites repérées dans vos documents (TVA, CFE, assemblées…) surveillées par la commande `/echeances`.

Le retour d'expérience complet, avec l'architecture et les chiffres : [Un assistant documentaire IA pour trois sociétés](https://www.dgu-consulting.fr/blog/assistant-documentaire-ia).

## Besoin d'aide

Vous voulez le mettre en place sans vous en occuper, l'adapter à votre situation, ou simplement en parler avant de vous lancer ?

**Point IT offert, 30 minutes en visio, sans engagement :** [réserver un créneau](https://calendly.com/serdar-arikan-dgu-consulting/30min)

Serdar Arikan · [DGU Consulting](https://www.dgu-consulting.fr) · [LinkedIn](https://www.linkedin.com/in/serdar-arikan)

---

*Pour les habitués de git : `git clone https://github.com/DGUCons/kit-assistant-documentaire.git`, puis la même phrase dans votre assistant, qui utilisera le clone local. Le détail des versions est dans le [CHANGELOG](CHANGELOG.md).*
