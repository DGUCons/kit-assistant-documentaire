# /rechercher <question> : retrouver une information dans l'index

## Garde-fous

- Toute recherche passe par l'index (`00_CONTEXTE/index.db`), jamais par une relecture des documents (le contenu extrait est déjà en base).
- Une information absente de l'index est annoncée comme absente. Jamais d'invention, jamais de comblement.
- N'ouvrir un document source que pour vérifier un détail précis sur un petit nombre de résultats, jamais en masse.

## Déroulé

1. Traduire la question en requêtes : recherche plein texte (`fichiers_fts`, syntaxe FTS5) + filtres sur les colonnes (structure, année, type, émetteur, montants, statut).
2. Croiser les résultats, trier par pertinence, garder les fiches réellement utiles.
3. Si besoin de certitude sur un détail : ouvrir le ou les documents concernés (pas plus de quelques-uns) et citer précisément.

## Restitution (format 7 points, si pertinent)

1. Réponse courte · 2. Faits confirmés (avec chiffres) · 3. Hypothèses · 4. Points à vérifier · 5. Documents sources (chemins) · 6. Action recommandée · 7. Le cas échéant, question à poser au cabinet comptable.
