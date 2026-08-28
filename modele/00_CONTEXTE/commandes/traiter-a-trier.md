# /traiter-a-trier [structure] : traiter les nouveaux dépôts

## Garde-fous (à relire avant chaque exécution)

- Lecture réelle de chaque document avant qualification (RG.1). Jamais de classement au nom de fichier.
- Au-delà de 5 fichiers : présenter le plan complet (fichier → destination + nouveau nom) et attendre validation avant de déplacer quoi que ce soit.
- Doute → `a_valider/` + `.txt` jumeau (RG.2). Jamais de décision silencieuse.
- Corbeille uniquement sur doublon prouvé par empreinte SHA-256 avec original conservé et indexé (RG.3).
- Jamais de dossier exclu, jamais d'original modifié, tout au journal (RG.5).

## Contexte à charger d'abord

`00_CONTEXTE/CONTEXTE_SOCIETES.md` · `00_CONTEXTE/REGLES_CLASSEMENT.md` · la base `00_CONTEXTE/index.db`.

## Déroulé

1. Lister le contenu des `a_trier/` de toutes les structures (ou de la structure passée en argument).
2. S'il n'y a rien : le dire en une phrase, terminer.
3. Lancer `00_CONTEXTE/_scripts/scan.py` sur les `a_trier/` concernés : enregistrement en base (empreinte, taille, dates, statut `a_lire`). Si l'empreinte existe déjà en base sur un original conservé : doublon prouvé → proposer la mise en corbeille (réversible), avec la fiche de l'original à l'appui.
4. Pour chaque fichier restant : lire le contenu réel, remplir la fiche (structure, date, type, émetteur, montants, résumé, mots-clés, confiance), proposer destination + nouveau nom (`AAAA-MM-JJ_type_tiers_objet.ext`).
5. Présenter le plan, attendre validation (obligatoire au-delà de 5 fichiers ; recommandé en dessous).
6. Exécuter : déplacer, renommer, puis mettre à jour la base : `chemin_origine` = ancien chemin, `chemin` = nouveau chemin absolu, statut `classe`, texte extrait en `fichiers_contenu`. Sans cette mise à jour du chemin, le prochain scan croirait le fichier disparu et le relirait à sa nouvelle place.
7. Journaliser (date, action, avant → après, raison) et mettre à jour `HANDOFF.md` si la session s'arrête là.

## Restitution

Tableau : fichier déposé → destination finale (ou a_valider/corbeille + raison). Compteurs : classés, en doute, doublons. Le cas échéant : questions pour l'utilisateur.
