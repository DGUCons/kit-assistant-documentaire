# Sécurité et confiance

Ce document explique les garde-fous du kit et, tout aussi important, ce qu'il faut savoir sur le trajet de vos données. Sans langue de bois.

## Ce que l'assistant ne fera jamais

Ces règles sont inscrites dans ses instructions permanentes (`CLAUDE.md`) et il doit les respecter même si on lui demande le contraire au fil d'une session :

1. **Supprimer définitivement un fichier.** Tout passe par la corbeille, réversible.
2. **Modifier ou écraser un document original.**
3. **Déclarer un doublon sans preuve.** Seule une empreinte SHA-256 identique (la signature unique d'un fichier) autorise la mise en corbeille d'une copie ; tout le reste est mis de côté avec explication écrite.
4. **Agir en masse sans plan validé.** Tout déplacement ou renommage en série est précédé d'un plan que vous approuvez.
5. **Écrire sur un système externe.** Banque comprise : lecture seule, toujours. Aucun virement, aucune modification, jamais.
6. **Lire un dossier exclu.** Les dossiers que vous désignez comme exclus (personnel, médical...) ne sont jamais ouverts.
7. **Inventer.** Une information absente des documents est signalée comme absente, pas comblée.

Et chaque action est journalisée, datée, dans `00_CONTEXTE/JOURNAL_ACTIONS.md` : vous pouvez tout retracer.

## Le trajet de vos données, honnêtement

- Vos documents restent **chez vous** (votre disque, votre cloud). Le kit n'envoie rien vers un serveur du kit : il n'y a pas de serveur du kit.
- En revanche, **quand l'assistant lit un document, son contenu transite par l'API de l'éditeur du modèle** (Anthropic pour Claude), comme pour toute utilisation de Claude. C'est le fonctionnement normal d'un assistant IA en ligne.
- Consultez la [politique de confidentialité d'Anthropic](https://www.anthropic.com/legal/privacy) et **vérifiez les réglages de confidentialité de votre compte** (notamment l'option concernant l'utilisation de vos données pour l'amélioration des modèles, réglable dans les paramètres du compte).
- Si certains documents ne doivent jamais transiter (données de santé, dossiers de tiers soumis au secret) : placez-les dans un dossier exclu, déclaré à l'installation. L'assistant ne l'ouvrira pas.
- Les identifiants et clés d'accès (banque, services en ligne) vivent **hors** du dossier documentaire, dans un emplacement que l'assistant ne lit pas.

## RGPD, en deux mots

Si vos documents contiennent des données personnelles de tiers (clients, salariés), vous restez responsable de traitement. Le bon réflexe : n'indexez que ce qui est nécessaire à votre gestion, excluez le superflu, et mentionnez cet outil dans votre registre de traitements si vous en tenez un. En cas de doute sur un cas précis, votre conseil habituel prime sur ce document.

## Ce que ce kit n'est pas

- Il ne tient pas votre comptabilité : il classe, retrouve et prépare.
- Il ne remplace ni votre expert-comptable, ni votre avocat. Il distingue toujours ce qui est confirmé par les documents, ce qui est une hypothèse, et ce qui doit être validé par un professionnel.
- Il n'est pas infaillible : c'est précisément pour ça que les garde-fous existent, que le dossier `a_valider/` existe, et que la décision finale vous revient.
