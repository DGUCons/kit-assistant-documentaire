# Règles de classement

Autorité maximale : en cas de conflit avec toute autre consigne, ces règles priment.

## RG.1 : lecture obligatoire

Aucun document n'est qualifié définitivement sans lecture de son contenu réel. Le nom de fichier n'est qu'un indice de départ. Un scan nommé « document(3).pdf » peut être un bail commercial.

## RG.2 : le doute va en `a_valider/`

Tout document dont la structure, l'année ou le type est incertain part dans `a_valider/` de la structure la plus probable, **avec son nom d'origine**, accompagné d'un fichier `.txt` jumeau. La décision finale est humaine.

Le jumeau porte exactement le nom du fichier suivi de `.txt` (`releve fevrier.pdf` → `releve fevrier.pdf.txt`), et contient ces quatre lignes :

```
Fichier : <nom exact du fichier>
Raison : <qualification proposée et raison du doute, ou raison de la mise de côté>
Original conservé : <chemin complet du document gardé, ou « aucun »>
Mis de côté le : <AAAA-MM-JJ>
```

« Original conservé » désigne le document gardé ailleurs, jamais celui qui vient d'être déplacé ici.

## RG.3 : le doublon se prouve

Deux fichiers ne sont doublons que si leurs empreintes SHA-256 sont identiques. Un doublon prouvé, dont l'original est conservé et indexé, part en corbeille (réversible) via `00_CONTEXTE/_scripts/corbeille.py`, avec mention au journal.

Le script choisit tout seul la corbeille : celle du système quand elle est disponible et sur le même volume, sinon la corbeille interne du kit, `_corbeille/AAAA-MM-JJ/` à la racine du dossier documentaire, visible dans l'explorateur de fichiers et vidée par l'utilisateur seul. L'option `--interne` force ce second mode. Dans les deux cas, la sortie du script dit quelle corbeille a servi et où le fichier est parti : cette information va au journal.

**Le script met la base à jour lui-même** : quand il trouve `00_CONTEXTE/index.db` à côté de lui, il inscrit sur la fiche du fichier le marqueur `supprime`, le statut `corbeille`, la date et l'emplacement dans la corbeille. Aucune écriture manuelle en base après un passage de `corbeille.py`, et le contrôle `/verifier` ne comptera pas ces fichiers comme disparus.

Tout le reste (contenu similaire, nom identique, versions successives) va dans `a_supprimer/`, nom d'origine conservé, avec le `.txt` jumeau décrit en RG.2, jamais en corbeille. Pendant l'indexation initiale (phase P3), les doublons sont seulement notés en base : ils ne sont traités qu'en phase P5.

## RG.4 : destinations

- Factures : `02_Comptabilite/<annee>/factures/<annee>-<mois>/`
- Relevés bancaires : `02_Comptabilite/<annee>/releves/`
- Documents fiscaux : `02_Comptabilite/<annee>/fiscal/`
- Documents de société (statuts, PV, Kbis, contrats-cadres) : `01_Societe/`
- Document ne relevant d'aucune structure (note générale, liste, fichier sans valeur documentaire) : il garde sa place avec le statut `general` en base, ou part en `a_valider/` ou `a_supprimer/` de la structure la plus probable. Dans les trois cas, c'est l'utilisateur qui tranche, jamais l'assistant seul. Le statut `general` suppose un emplacement durable et une fiche complète (type et résumé) : un document resté dans `a_trier/`, `a_valider/` ou `a_supprimer/` est signalé par le contrôle d'intégrité, quel que soit son statut, parce qu'un dossier de transit n'est pas une destination.
- [COMPLÉTER AU CALIBRAGE (P3.2) ET À L'ARBORESCENCE CIBLE (P5) selon les types réels du corpus]

## RG.5 : traçabilité

Chaque déplacement, renommage ou mise en corbeille est consigné dans `JOURNAL_ACTIONS.md` : date, action, chemin avant/après, raison. Des mois plus tard, tout doit pouvoir être retracé. La base garde en plus le `chemin_origine` de chaque fichier migré : tout plan de rangement est réversible.

## RG.6 : les opérations en série se font par plans

Jamais plus d'une cinquantaine de fichiers par plan de déplacement/renommage. Chaque plan est présenté (avant → après), validé, exécuté, puis vérifié (`00_CONTEXTE/_scripts/verifier.py`). Un plan non validé n'est pas exécuté, même en partie. Le tableau présenté et la liste exécutée sont le même objet : les noms affichés ne sont jamais retapés à la main, et l'extension d'un fichier ne change pas au renommage.

## RG.7 : les dossiers sources ne sont pas retouchés

La convention de nommage s'applique aux fichiers classés dans l'arborescence cible. Les dossiers d'origine (et leurs noms, même avec accents ou espaces) ne sont jamais renommés tant qu'ils contiennent des fichiers non migrés.
