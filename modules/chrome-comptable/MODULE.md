# Module cabinet en ligne : consultation via le navigateur (Claude Code uniquement)

> Mode d'emploi suivi par l'assistant au moment de l'activation. Ce module repose sur l'extension **Claude in Chrome** : il n'est **pas disponible** avec un autre assistant (Codex, Gemini) : dans ce cas, le dire simplement et ne pas l'activer.

## Ce que le module permet

Consulter, avec l'utilisateur, l'interface en ligne de son cabinet ou de son outil comptable (Dougs, Indy, Pennylane, Cegid…), en lecture : vérifier les pièces en attente de validation, repérer un justificatif manquant, télécharger un document pour le classer.

## Règles du module (non négociables)

- **Lecture et téléchargement uniquement.** Aucune saisie comptable, aucune validation d'écriture, aucune télédéclaration, aucun paiement, aucune modification de paramètres, même sur demande au fil de l'eau : signaler et laisser l'utilisateur faire lui-même ce geste.
- L'utilisateur reste connecté avec **son** compte, dans **son** navigateur : l'assistant ne demande jamais les identifiants du cabinet et ne les stocke jamais.
- Chaque session de consultation est journalisée (date, ce qui a été consulté, ce qui a été téléchargé).

## Activation, pas à pas

1. **Consentement** : expliquer le périmètre (le paragraphe ci-dessus) et attendre un accord explicite.
2. **Installation** : guider l'installation de l'extension Claude in Chrome depuis la page officielle d'Anthropic, et sa connexion au compte Claude de l'utilisateur.
3. **Test en lecture** : l'utilisateur se connecte à son interface comptable ; l'assistant consulte une page convenue (ex. la liste des pièces en attente) et restitue ce qu'il voit.
4. **Enregistrement** : noter le module actif (nom du cabinet et de l'interface) dans la section « Modules actifs » des trois fichiers d'instructions et dans `CONTEXTE_SOCIETES.md`. Journaliser.

## Usage courant

- Avant un envoi de pièces : croiser la liste des manquants de `/preparer-comptable` avec ce que l'interface affiche.
- Un document présent dans l'interface mais absent du classement : le télécharger dans le `a_trier/` de la structure, puis `/traiter-a-trier`.
