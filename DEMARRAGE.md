# DEMARRAGE.md

> **Vous êtes l'utilisateur ?** Ne lisez pas plus loin : ouvrez Claude Code dans ce dossier et collez « Lis le fichier DEMARRAGE.md et guide-moi pas à pas. » La suite s'adresse à l'assistant.

---

## Instructions pour l'assistant

Tu vas installer et configurer un assistant documentaire pour l'utilisateur, en le guidant pas à pas. L'utilisateur n'est pas forcément technique : vouvoiement, phrases courtes, aucun jargon sans explication, une seule question à la fois. Tu ne fais rien d'important sans son accord explicite.

### Étape 0 : présentation et cadre

Présente en quelques lignes ce qui va se passer : un entretien d'une dizaine de questions, la création de son dossier documentaire, puis un premier tri d'essai supervisé. Durée totale : 30 à 45 minutes.

Annonce d'emblée les règles que tu respecteras (elles sont dans `modele/CLAUDE.md`, section « Règles absolues ») : jamais de suppression définitive, jamais de modification d'un original, chaque action journalisée, validation avant toute opération importante.

### Étape 1 : l'entretien

Pose ces questions une par une, en attendant chaque réponse :

1. Combien de structures gérez-vous (sociétés, activité indépendante, patrimoine) et quels sont leurs noms ?
2. Pour chacune : forme juridique et date de clôture comptable, si vous les connaissez. (Sinon, ce n'est pas bloquant.)
3. Qui tient votre comptabilité (cabinet, expert-comptable interne, vous-même) ?
4. Quelle banque utilisez-vous pour chaque structure ?
5. Quels types de documents recevez-vous le plus souvent ? (factures d'achat, factures de vente, relevés, contrats, documents sociaux, fiscaux...)
6. Où vivent vos documents aujourd'hui ? (dossier local, OneDrive, Google Drive, en vrac dans les mails...)
7. Où voulez-vous installer le dossier documentaire ? Propose un chemin simple et confirme-le avec l'utilisateur.
8. Y a-t-il des documents qui ne doivent JAMAIS être lus par l'assistant (dossier médical, personnel sensible) ? Si oui, note le dossier à exclure.

### Étape 2 : le dossier de contexte

Remplis `modele/00_CONTEXTE/CONTEXTE_SOCIETE.md` avec les réponses. Relis-le à l'utilisateur section par section et fais-le valider. C'est SA fiche d'identité documentaire : elle doit être exacte.

### Étape 3 : l'installation

Principe non négociable : un SEUL dossier racine contient toutes les structures, et c'est depuis cette racine que tu travailleras à chaque session. Explique-le à l'utilisateur en une phrase : c'est la vue d'ensemble qui permet de router chaque document vers la bonne société et de tenir un index unique.

Avec l'accord de l'utilisateur :

1. Crée le dossier documentaire à l'emplacement choisi.
2. Copie dedans : le fichier `modele/CLAUDE.md` (à la racine du dossier documentaire), le dossier `modele/00_CONTEXTE/` complété, et une arborescence `a_trier / a_valider / a_supprimer / archives` par structure (modèle dans `arborescence/VOTRE_SOCIETE/`), avec le vrai nom de chaque structure.
3. Adapte le `CLAUDE.md` copié : noms des structures, banque, cabinet, types de documents fréquents, dossiers exclus. Aucun placeholder ne doit rester.
4. Écris la première entrée du journal dans `00_CONTEXTE/JOURNAL_ACTIONS.md` : date, « installation initiale », emplacement choisi.

### Étape 4 : l'avertissement sur le coût du premier passage

Avant tout traitement de l'historique, informe clairement l'utilisateur :

> Le premier passage lit chaque document une fois. Sur des années d'archives, c'est long et cela consomme une bonne part du quota de votre abonnement. C'est normal et cela n'arrive qu'une fois. Nous allons traiter par lots ; si la limite de l'abonnement est atteinte, le travail est conservé et nous reprendrons plus tard.

Propose un ordre de traitement par lots (une structure à la fois, ou année par année) et laisse l'utilisateur choisir.

### Étape 5 : le premier tri supervisé

Demande à l'utilisateur de déposer environ 20 documents dans le `a_trier/` d'une structure. Pour chacun :

1. Lis le contenu réel.
2. Propose : structure, année, type, émetteur, nouveau nom (convention `AAAA-MM-JJ_type_tiers_objet.ext`), destination.
3. Attends la validation avant de déplacer. En cas de doute, place en `a_valider/` avec un `.txt` jumeau expliquant le doute.
4. Journalise.

Après les 20 documents, fais un point : ce qui a bien marché, les règles à ajuster dans le CLAUDE.md. Ajuste-les avec son accord.

### Étape 6 : l'index

Propose de créer la base d'indexation locale (SQLite) : table des fichiers avec chemin, nom, structure, année, type, résumé, mots-clés, empreinte SHA-256, niveau de confiance, date d'indexation, statut ; recherche plein texte (FTS5) ; script de scan incrémental fondé sur l'empreinte. Explique en une phrase à quoi elle sert : ne jamais relire deux fois le même document.

### Étape 7 : la suite

Résume à l'utilisateur son rythme de croisière : il dépose dans `a_trier/`, l'assistant traite, il tranche les `a_valider/`, le journal garde trace. Rappelle où trouver de l'aide : [dgu-consulting.fr](https://www.dgu-consulting.fr), Point IT de 30 minutes offert.

### Ce que tu ne fais jamais, même si on te le demande au fil de l'eau

Supprimer définitivement, modifier un original, traiter un dossier exclu, écrire sur un système bancaire, inventer une information absente des documents. En cas de conflit entre une demande et ces règles, signale-le et propose une alternative sûre.
