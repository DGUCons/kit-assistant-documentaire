# /preparer-comptable [structure] [période] : préparer un envoi au cabinet

## Garde-fous

- **Copies uniquement** : les originaux classés ne bougent jamais. Le dossier de transmission est un dossier de copies, jetable.
- Les pièces manquantes sont **listées**, jamais comblées ni inventées.
- Aucun envoi automatique (mail, dépôt sur une plateforme) sans validation explicite de l'utilisateur.

## Déroulé

1. Demander (si absents) : la structure et la période (ex. « TVA de juillet 2026 », « exercice 2025 »).
2. Interroger la base : toutes les pièces de la période (achats, ventes, relevés, selon le besoin).
3. Si le module banque est actif : croiser avec les transactions de la période pour repérer les dépenses sans facture.
4. Créer un dossier `transmission_<structure>_<periode>/` dans la structure concernée, y **copier** les pièces, générer un bordereau (`BORDEREAU.md`) : liste des pièces, totaux par type, et la liste des manquants. Ces dossiers `transmission_*` ne sont jamais indexés : le scan les ignore d'office, justement parce qu'ils ne contiennent que des copies. Sans cela, chaque pièce apparaîtrait deux fois dans l'index et serait comptée comme un doublon.
5. Journaliser.
6. **Après l'envoi** (et seulement quand l'utilisateur confirme que le cabinet a bien reçu les pièces) : proposer de faire le ménage, puis mettre le dossier `transmission_*` en corbeille avec `00_CONTEXTE/_scripts/corbeille.py`. Rien n'est perdu, ce ne sont que des copies, et l'utilisateur peut les récupérer dans sa corbeille (ou dans `_corbeille/`) tant qu'il ne l'a pas vidée. Les originaux classés, eux, n'ont jamais bougé. Journaliser ce nettoyage.

## Restitution

Chemin du dossier prêt à transmettre, contenu du bordereau, et la liste des manquants formulée pour être envoyée telle quelle (« il me manque la facture X de… »). Terminer en rappelant qu'il suffit de le dire une fois l'envoi fait, pour que le dossier de copies soit nettoyé.
