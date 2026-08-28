# Module enrichissement légal : informations officielles d'une entreprise

> Utilisé pendant l'entretien d'installation (START.md, phase P1.2) et à chaque nouvelle structure. Sources publiques, lecture seule.

## Ce que le module fait

À partir du nom d'une entreprise (ou d'un lien fourni par l'utilisateur vers sa page societe.com ou Pappers), retrouver ses informations officielles : SIREN, forme juridique, code d'activité (APE), siège, date de création, dirigeants publiés.

## Ordre des sources

1. **Annuaire public des entreprises** (annuaire-entreprises.data.gouv.fr) via son API gratuite et sans clé : `python3 <kit>/modules/enrichissement-legal/enrichir.py "nom de l'entreprise"`, où `<kit>` est `.kit/` une fois l'installation faite, ou l'emplacement temporaire de téléchargement pendant l'entretien initial (START.md P1.2, avant que `.kit/` existe).
2. En complément de vérification, ou si l'utilisateur fournit un lien : Pappers, societe.com (consultation simple).

**Plusieurs candidats ?** Toujours en langage courant : dire « société active » ou « société cessée » (jamais les codes bruts), et proposer de filtrer par ville ou département (« laquelle est la vôtre ? celle de Rennes ou celle de Tours ? »). Une non-technicienne ne doit jamais avoir à décoder une fiche INSEE.

## Règles du module (non négociables)

- **Validation humaine anti-homonymes** : chaque fiche candidate est présentée (nom exact, SIREN, ville, dirigeant publié) et validée par l'utilisateur AVANT tout enregistrement en base ou dans le contexte. Ne jamais trancher entre deux homonymes à sa place.
- Un SIREN ne s'invente pas et ne se devine pas. Introuvable → demander à la main ; « à vérifier » est accepté.
- La date de clôture comptable n'est pas toujours publiée : si absente, la demander à l'utilisateur (elle figure sur ses statuts ou sa dernière liasse).

## Après validation

Enregistrer dans la table `entites` (siren, forme_juridique, code_ape…) et refléter dans `00_CONTEXTE/CONTEXTE_SOCIETES.md`, avec la mention de la source. Journaliser.
