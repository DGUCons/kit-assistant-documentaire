# Sécurité et confiance

Ce document explique les garde-fous du kit et, tout aussi important, ce qu'il faut savoir sur le trajet de vos données. Sans langue de bois.

## Ce que vous installez, exactement

Le kit ne contient **que des fichiers texte lisibles** : des instructions en français (fichiers `.md`) et quelques petits scripts Python (`.py`) que vous pouvez ouvrir avec n'importe quel éditeur. Zéro exécutable, zéro installateur, zéro macro, zéro composant caché. Tout est public sur GitHub : vous pouvez tout lire **avant** d'installer quoi que ce soit. C'est aussi pour cela que vous n'avez rien à télécharger vous-même : votre assistant récupère ces fichiers texte, vous montre ce qu'il fait, et vous validez.

## Ce que l'assistant ne fera jamais

Ces règles sont inscrites dans ses instructions permanentes et il doit les respecter même si on lui demande le contraire au fil d'une session :

1. **Supprimer définitivement un fichier.** Tout passe par la corbeille de votre système, réversible. Le script de mise en corbeille est d'ailleurs testé sur un fichier témoin dès l'installation.
2. **Modifier ou écraser un document original.**
3. **Déclarer un doublon sans preuve.** Seule une empreinte SHA-256 identique (la signature unique d'un fichier) autorise la mise en corbeille d'une copie ; tout le reste est mis de côté avec explication écrite.
4. **Agir en masse sans plan validé.** Tout déplacement ou renommage en série est précédé d'un plan que vous approuvez, par lots courts, et le chemin d'origine de chaque fichier est conservé : chaque plan est réversible.
5. **Écrire sur un système externe.** Banque comprise : lecture seule, toujours. Aucun virement, aucune saisie, aucune validation en ligne, jamais. Sur l'interface de votre cabinet comptable (module optionnel) : consultation et téléchargement uniquement.
6. **Lire un dossier exclu.** Les dossiers que vous désignez comme exclus (personnel, médical…) ne sont jamais ouverts.
7. **Inventer.** Une information absente des documents est signalée comme absente, pas comblée.

Et chaque action est journalisée, datée, dans `00_CONTEXTE/JOURNAL_ACTIONS.md` : vous pouvez tout retracer.

Au tout premier lancement, l'assistant **audite aussi vos réglages existants** (vos fichiers d'instructions personnels) et vous signale toute consigne qui entrerait en conflit avec ces règles, avant de commencer.

## Le trajet de vos données, honnêtement

- Vos documents restent **chez vous** (votre disque, votre cloud). Le kit n'envoie rien vers un serveur du kit : il n'y a pas de serveur du kit.
- En revanche, **quand l'assistant lit un document, son contenu transite par l'API de l'éditeur du modèle** (Anthropic pour Claude), comme pour toute utilisation d'un assistant IA en ligne. C'est le fonctionnement normal.
- Consultez la [politique de confidentialité d'Anthropic](https://www.anthropic.com/legal/privacy) et **vérifiez les réglages de confidentialité de votre compte** (notamment l'option concernant l'utilisation de vos données pour l'amélioration des modèles, réglable dans les paramètres du compte). Avec un autre éditeur (OpenAI, Google), le principe est le même : vérifiez ses réglages.
- Si certains documents ne doivent jamais transiter (données de santé, dossiers de tiers soumis au secret) : placez-les dans un dossier exclu, déclaré à l'installation. L'assistant ne l'ouvrira pas.
- Les identifiants et clés d'accès (banque, services en ligne) vivent **hors** du dossier documentaire (par exemple `~/.config/assistant-doc/`), ne sont jamais mis en base, jamais affichés, jamais journalisés. La base ne stocke que les 4 derniers caractères d'un IBAN.

## RGPD, en deux mots

Si vos documents contiennent des données personnelles de tiers (clients, salariés), vous restez responsable de traitement. Le bon réflexe : n'indexez que ce qui est nécessaire à votre gestion, excluez le superflu, et mentionnez cet outil dans votre registre de traitements si vous en tenez un. En cas de doute sur un cas précis, votre conseil habituel prime sur ce document.

## Ce que ce kit n'est pas

- Il ne tient pas votre comptabilité : il classe, retrouve et prépare.
- Il ne remplace ni votre expert-comptable, ni votre avocat. Il distingue toujours ce qui est confirmé par les documents, ce qui est une hypothèse, et ce qui doit être validé par un professionnel.
- Il n'est pas infaillible : c'est précisément pour ça que les garde-fous existent, que le dossier `a_valider/` existe, et que la décision finale vous revient.
