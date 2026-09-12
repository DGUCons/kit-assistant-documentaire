# /point-etat : où en est le système

## Garde-fous

Lecture seule intégrale : cette commande ne modifie rien, nulle part.

## Déroulé

1. Lire `00_CONTEXTE/HANDOFF.md` et les tables `meta`, `lots`, `sources` de la base.
2. Compter en base : documents indexés / restants à lire / en `a_valider` / en `a_supprimer` / généraux (rattachés à aucune structure, statut `general`) / illisibles / non disponibles.
3. Regarder le contenu réel des dossiers `a_trier/` et `a_valider/` de chaque structure (un simple listage).
4. Lire les échéances à venir (table `echeances`, 60 prochains jours) et les dépassées non faites.
5. Si `.kit/` est présent et le réseau disponible : comparer `00_CONTEXTE/VERSION_KIT` à la version publiée (`https://raw.githubusercontent.com/DGUCons/kit-assistant-documentaire/main/VERSION`). Si une mise à jour existe, le signaler en une phrase (sans l'appliquer : c'est `/mettre-a-jour` qui s'en charge).

## Restitution

Cinq lignes maximum par bloc : avancement de l'installation (phase), santé du classement (compteurs), dépôts en attente, échéances proches, version du kit. Terminer par le prochain pas recommandé.
