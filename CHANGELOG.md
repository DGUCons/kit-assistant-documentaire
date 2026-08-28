# Changelog

## v2.0.0 (2026-08-28)

Refonte complète : l'installation tient désormais en **une seule phrase à coller**, plus aucun téléchargement manuel.

- Nouveau bootstrap `START.md` : l'assistant télécharge le kit lui-même et déroule sept phases (pré-vol, entretien, installation, indexation, questions, rangement, rythme de croisière), avec reprise multi-sessions (« Reprenons ») garantie document par document
- Entretien enrichi : recherche automatique des informations légales (SIREN, forme, APE) sur l'annuaire public des entreprises avec validation anti-homonymes, cartographie complète des sources documentaires (local, cloud, mails, papier), audit des réglages d'assistant existants avant tout travail
- Base d'indexation étendue : entités, sources, montants, échéances, transactions bancaires, lots de reprise ; recherche plein texte ; chemin d'origine conservé (tout rangement est réversible)
- Dix commandes installées : `/traiter-a-trier`, `/rechercher`, `/point-etat`, `/reprendre`, `/echeances`, `/rapprocher`, `/preparer-comptable`, `/indexer`, `/verifier`, `/mettre-a-jour`
- Trois modules optionnels : rapprochement bancaire en lecture seule (Qonto en référence), consultation du cabinet en ligne via le navigateur (Claude uniquement), enrichissement légal
- Multi-assistants : instructions générées pour Claude Code, Codex et Gemini CLI (conçu et testé avec Claude Code uniquement ; les autres parcours sont acceptés et annoncés comme non testés)
- Multi-OS consolidé : corbeille native réversible Windows/macOS, détection des fichiers OneDrive « dans le nuage seulement », scripts en bibliothèque standard Python uniquement
- Mise à jour maîtrisée : `/mettre-a-jour` ne remplace que les fichiers du kit (séparation publique dans `MANIFESTE.txt`), jamais vos adaptations ni votre base

## v1.0.0 (2026-07-06)

Première version publique.

- Installation guidée par l'assistant (DEMARRAGE.md) : entretien, contexte, arborescence, premier tri supervisé
- Fichier d'instructions complet avec les 10 règles de sécurité
- Convention de nommage et règles de classement
- Index local SQLite (lecture unique de chaque document, scan incrémental par empreinte)
- Documentation : installation Windows/macOS, sécurité et trajet des données, FAQ
