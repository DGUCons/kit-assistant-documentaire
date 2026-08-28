# Module banque : rapprochement bancaire en lecture seule

> Mode d'emploi suivi par l'assistant au moment de l'activation (proposée à l'entretien, activée en rythme de croisière). Prérequis : une banque qui expose une API. Qonto est la référence testée ; pour une autre banque à API, adapter le script sur le même modèle (lecture seule stricte).

## Règles du module (non négociables)

- **Lecture seule absolue** : le script n'émet que des requêtes de consultation. Aucune écriture, aucun virement, aucune validation, jamais, même sur demande expresse.
- La clé d'accès vit **hors du dossier documentaire** : `~/.config/assistant-doc/qonto.json`. Elle n'est jamais affichée, jamais copiée dans le dossier documentaire, jamais mise en base.
- En base ne vivent que : la banque, les 4 derniers caractères de l'IBAN (`iban_masque`), les transactions.

## Activation, pas à pas

1. **Consentement** : expliquer à l'utilisateur ce que le module fait (relier chaque facture à son paiement) et ce qu'il ne fera jamais (le paragraphe ci-dessus). Attendre un accord explicite.
2. **Création de la clé** (l'utilisateur agit, l'assistant guide) : dans l'interface Qonto, réglages de l'organisation, section « Clé API » : noter l'identifiant (login) et la clé secrète. Recommander une clé en **lecture seule** si l'offre le propose.
3. **Stockage** : créer `~/.config/assistant-doc/qonto.json` :
   ```json
   {"login": "identifiant-organisation", "secret_key": "la-cle"}
   ```
   L'assistant crée le fichier mais ne relit jamais la clé à voix haute.
4. **Déclaration des comptes** : vérifier que chaque compte est dans la table `comptes_bancaires` avec son `iban_masque` (4 derniers caractères). Compléter si besoin, avec validation.
5. **Test** : lancer `python3 .kit/modules/banque/qonto_lecture.py` depuis la racine documentaire. Restituer le résultat (comptes reconnus, transactions ramenées).
6. **Enregistrement** : noter le module comme actif dans la section « Modules actifs » des trois fichiers d'instructions et dans `CONTEXTE_SOCIETES.md`. Journaliser l'activation.

## Usage courant

La commande `/rapprocher` (fiche `00_CONTEXTE/commandes/rapprocher.md`) : synchronisation, rapprochement automatique des correspondances sûres, propositions pour les incertaines, liste des dépenses sans justificatif.
