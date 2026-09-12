# /rapprocher [structure] [période] : rapprochement bancaire (module banque requis)

## Garde-fous

- **Lecture seule absolue** sur la banque : aucune écriture, aucun virement, aucune modification, même sur demande au fil de l'eau. Signaler et refuser.
- La clé d'accès vit HORS du dossier documentaire (voir `.kit/modules/banque/MODULE.md`) : ne jamais l'afficher, la copier ni la déplacer.
- Une correspondance incertaine est **proposée**, jamais imposée : statut `incertain`, décision humaine.
- Module non activé → expliquer comment l'activer (`.kit/modules/banque/MODULE.md`) et s'arrêter là.

## Déroulé

1. Vérifier que le module est actif (section « Modules actifs » des instructions permanentes).
2. Lancer la synchronisation en lecture seule (`.kit/modules/banque/qonto_lecture.py` ou équivalent) : les nouvelles transactions arrivent dans la table `transactions` (l'identifiant côté banque évite tout doublon).
3. Rapprocher automatiquement ce qui est sûr : montant exact + date proche + émetteur/libellé concordants → lier `transactions.fichier_id`, statut `rapproche`.
4. Proposer les correspondances plausibles mais non certaines (statut `incertain`) **dans un seul tableau**, puis une seule question : « 1. Tout lier ainsi (ma recommandation) / 2. Les reprendre une par une ». Jamais une question par transaction sans que l'utilisateur ait choisi le pas à pas.
5. Lister les transactions restées sans justificatif, groupées par contrepartie, avec la période.

## Restitution

Compteurs : rapprochées / incertaines (à trancher) / sans justificatif. Puis la liste des justificatifs manquants, exploitable telle quelle pour réclamer les factures. Journaliser la session de rapprochement.
