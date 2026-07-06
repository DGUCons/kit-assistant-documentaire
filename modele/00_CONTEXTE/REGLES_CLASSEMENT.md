# Règles de classement

Autorité maximale : en cas de conflit avec une autre consigne, ces règles priment.

## RG.1 : lecture obligatoire

Aucun document n'est qualifié définitivement sans lecture de son contenu réel. Le nom de fichier n'est qu'un indice de départ. Un scan nommé « document(3).pdf » peut être un bail commercial.

## RG.2 : le doute va en `a_valider/`

Tout document dont la structure, l'année ou le type est incertain part dans `a_valider/` de la structure la plus probable, accompagné d'un fichier `.txt` jumeau : origine, qualification proposée, raison du doute. La décision finale est humaine.

## RG.3 : le doublon se prouve

Deux fichiers ne sont doublons que si leurs empreintes SHA-256 sont identiques. Un doublon prouvé, dont l'original est conservé et indexé, peut être mis en corbeille (réversible) avec mention au journal. Tout le reste (contenu similaire, nom identique, versions) va dans `a_supprimer/` avec `.txt` explicatif, jamais en corbeille.

## RG.4 : destinations

- Factures : `02_Comptabilite/<annee>/factures/<annee>-<mois>/` ; pour les ventes, le mois retenu est celui du paiement (sinon `en_attente_paiement/`)
- Documents de société (statuts, PV, contrats-cadres) : `01_Societe/`
- [COMPLÉTER LORS DE L'INSTALLATION selon votre arborescence]

## RG.5 : traçabilité

Chaque déplacement, renommage ou mise en corbeille est consigné dans `JOURNAL_ACTIONS.md` : date, action, chemin avant/après, raison. Des mois plus tard, tout doit pouvoir être retracé.
