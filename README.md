# Gestion des Déplacements (Odoo)

Module Odoo complet pour gérer les demandes de déplacement et missions des employés, le suivi des frais, les validations hiérarchiques (Manager → DAF), et la logistique (villes, véhicules de service, modes de transport). Le module s’appuie sur les apps `base`, `mail` et `hr`.

Auteur: Ahmed Raji

## Fonctionnalités
- **Demandes de déplacement**: création, soumission, approbation (Manager), prise en charge et clôture (DAF), refus avec motif, annulation.
- **Calculs automatiques**: nombre de jours, caractère international (comparaison pays ville vs société), frais journaliers (barème national/international), classe de voyage pour avion selon distance.
- **Logistique**: gestion des **villes** (avec pays, contrainte d’unicité) et des **véhicules de service**.
- **Notifications & suivi**: chatter, activités assignées aux responsables, emails automatiques (soumis, approuvé, notification DAF).
- **Sécurité et rôles**: groupes Manager et DAF avec droits adaptés; règles métier limitant qui peut créer pour qui.
- **Séquences**: attribution automatique des références de demandes via `ir.sequence`.

## Modèles de données
- `gestion.deplacement.demande` (Demande de déplacement)
	- Principaux champs: `name` (référence), `employee_id`, `manager_id`, `date_debut`, `date_fin`, `destination_city_id`, `mode_transport`, `distance_estimee`, `vehicule_id`, `nb_jours`, `is_international`, `montant_frais`, `mission_objet`, `ordre_mission_file`, `ordre_mission_filename`, `state`, `motif_refus`, `currency_id`, `company_id`, `active`.
	- Inherit: `mail.thread`, `mail.activity.mixin`.
	- États: `brouillon`, `soumis`, `approuve`, `en_cours`, `termine`, `refuse`, `annule`.
	- Actions: `action_submit`, `action_approve`, `action_refuse` (ouvre le wizard), `action_process`, `action_complete`, `action_cancel`, `action_reset_draft`.
	- Contraintes métier: cohérence dates, distance > 0, avion ≥ 500 km, véhicule obligatoire si mode « véhicule de service », contrôle de création par l’employé selon groupe.

- `gestion.deplacement.ville`
	- Champs: `name`, `country_id` (requis), `code_postal`, `active`.
	- Contrainte: unicité `(name, country_id)`; `name_get` affiche « Ville, Pays ».

- `gestion.deplacement.service.vehicule`
	- Champs: `name`, `immatriculation`, `marque`, `modele`, `company_id`, `active`.

## Vues et menus
- `views/ville_view.xml`: liste/formulaire des villes.
- `views/demande_deplacement_view.xml`: liste/formulaire des demandes, boutons d’actions selon état et rôle.
- `views/service_vehicule_view.xml`: liste/formulaire des véhicules de service.
- `views/menu.xml`: menu principal Gestion des Déplacements + sous-menus.

## Wizard
- `wizard/demande_refus_wizard.py` et `wizard/demande_refus_wizard_view.xml`: saisie du **motif de refus** par le Manager; met à jour la demande et passe l’état à `refuse`.

## Données et emails
- `data/sequence.xml`: séquence `gestion.deplacement.demande` pour générer les références.
- `data/ville_data.xml`: jeux de villes initiaux.
- `data/service_vehicule_data.xml`: jeux de véhicules initiaux.
- `data/email_templates.xml`: templates pour demande soumise, approuvée (employé), approuvée (notification DAF).

## Sécurité
- `security/deplacement_security.xml`: déclarations des groupes (ex. `group_deplacement_manager`, `group_deplacement_daf`).
- `security/ir.model.access.csv`: droits d’accès sur les modèles selon groupes.

## Workflow fonctionnel
1. **Employé** crée en `brouillon` et joint l’**ordre de mission** (PDF).
2. **Soumission** → état `soumis`, notification au **Manager** (activité + email si configuré).
3. **Manager**: approuve → `approuve` (emails à employé + DAF), ou refuse via wizard → `refuse` (avec motif).
4. **DAF**: prend en charge → `en_cours`, puis **termine** → `termine`.
5. Possibilité **d’annuler** ou **de remettre en brouillon** une demande refusée.

## Installation
Prérequis: Odoo avec modules `base`, `mail`, `hr`.

1. Placer ce dossier dans `addons` d’Odoo (déjà le cas ici).
2. Mettre à jour la liste des apps, puis installer « Gestion des Déplacements ».
3. Vérifier que les groupes et accès sont correctement appliqués.

## Configuration
- **Société**: renseigner le **pays** de la société (`res.company.country_id`) pour le calcul `is_international`.
- **Email**: configurer le serveur de messagerie sortant pour l’envoi des templates.
- **HR**: associer les utilisateurs à leurs **employés** et managers (`hr.employee.parent_id`).
- **Séquences**: la séquence `gestion.deplacement.demande` est fournie; ajuster si besoin.

## Utilisation rapide
- Créer des **villes** et **véhicules de service** si nécessaire.
- En tant qu’employé, créer une **demande**, remplir les champs requis, joindre l’**ordre de mission**, puis **soumettre**.
- En tant que **Manager**, approuver ou refuser (via wizard avec motif).
- En tant que **DAF**, traiter (`en_cours`) et **terminer**.

## Tests et vérifications
- Valider les règles métier: dates (fin ≥ début), distance > 0, avion ≥ 500 km, cohérence du véhicule.
- Vérifier le calcul automatique des **jours**, **frais**, **classe avion**, et le statut **international** selon le pays.
- Confirmer la réception des **emails** et la création des **activités**.

## Limites et évolutions possibles
- Barèmes de frais codés en dur (700/1500) → externaliser via paramètres ou grille.
- Affectation DAF: aujourd’hui via groupe; pourrait être par département ou par file d’attente.
- Ajout de pièces jointes multiples, workflow multi-niveaux, intégration comptable (notes de frais).

## Licence
LGPL-3
