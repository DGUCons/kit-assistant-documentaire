# Passation entre sessions (HANDOFF)

> Réécrit par l'assistant à chaque fin de lot et fin de phase. C'est la première chose lue en début de session, avant même la base. En cas d'écart avec les tables `meta` et `lots` de la base, la base fait foi (elle est plus fraîche d'au plus un lot).

## État au [DATE ET HEURE]

- **Phase en cours** : [P0 à P6, ou « terminee »]
- **Dernier point atteint** : [ex. « source OneDrive : lot 7 terminé, 214 documents indexés sur 391 »]
- **Prochain pas concret** : [ex. « reprendre le lot 8 : 12 fichiers a_lire restants sur cette source »]
- **Décisions en attente de l'utilisateur** : [liste, ou « aucune »]
- **Remarques** : [tout ce que la prochaine session doit savoir]

## Phrase de reprise

Ouvrez votre assistant dans le dossier racine et dites : **Reprenons**
