# /preparer-comptable [structure] [période] : préparer un envoi au cabinet

## Garde-fous

- **Copies uniquement** : les originaux classés ne bougent jamais. Le dossier de transmission est un dossier de copies, jetable.
- Les pièces manquantes sont **listées**, jamais comblées ni inventées.
- Aucun envoi automatique (mail, dépôt sur une plateforme) sans validation explicite de l'utilisateur.

## Déroulé

1. Demander (si absents) : la structure et la période (ex. « TVA de juillet 2026 », « exercice 2025 »).
2. Interroger la base : toutes les pièces de la période (achats, ventes, relevés, selon le besoin).
3. Si le module banque est actif : croiser avec les transactions de la période pour repérer les dépenses sans facture.
4. Créer un dossier `transmission_<structure>_<periode>/` dans la structure concernée, y **copier** les pièces, générer un bordereau (`BORDEREAU.md`) : liste des pièces, totaux par type, et la liste des manquants.
5. Journaliser.

## Restitution

Chemin du dossier prêt à transmettre, contenu du bordereau, et la liste des manquants formulée pour être envoyée telle quelle (« il me manque la facture X de… »).
