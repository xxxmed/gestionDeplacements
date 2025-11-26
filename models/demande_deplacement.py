# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DemandeDeplacement(models.Model):
    _name = 'gestion.deplacement.demande'
    _description = 'Demande de Déplacement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_debut desc, name desc'

    # Identification
    name = fields.Char(
        string='Référence',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: 'Nouveau'
    )
    
    # Employé et Manager
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employé',
        required=True,
        tracking=True,
        readonly=True,
        states={'brouillon': [('readonly', False)]},
        default=lambda self: self.env.user.employee_id
    )
    
    manager_id = fields.Many2one(
        'hr.employee',
        string='Manager',
        compute='_compute_manager_id',
        store=True,
        readonly=True
    )
    
    # Détails du voyage
    date_debut = fields.Date(
        string='Date de début',
        required=True,
        tracking=True
    )
    
    date_fin = fields.Date(
        string='Date de fin',
        required=True,
        tracking=True
    )
    
    destination_city_id = fields.Many2one(
        'gestion.deplacement.ville',
        string='Ville de destination',
        required=True,
        tracking=True
    )
    
    # Détails logistiques
    mode_transport = fields.Selection([
        ('train', 'Train'),
        ('autocar', 'Autocar'),
        ('avion', 'Avion'),
        ('vehicule_service', 'Véhicule de service')
    ], string='Mode de transport', required=True, tracking=True)
    
    distance_estimee = fields.Float(
        string='Distance estimée (Km)',
        required=True,
        tracking=True
    )
    
    vehicule_id = fields.Many2one(
        'gestion.deplacement.service.vehicule',
        string='Véhicule de service',
        tracking=True
    )
    
    # Classe de voyage pour l'avion
    classe_voyage = fields.Selection([
        ('economique', 'Classe économique'),
        ('business', 'Classe business')
    ], string='Classe de voyage', compute='_compute_classe_voyage', store=True)
    
    # Calculs automatiques
    nb_jours = fields.Integer(
        string='Nombre de jours',
        compute='_compute_nb_jours',
        store=True
    )
    
    is_international = fields.Boolean(
        string='Déplacement international',
        compute='_compute_is_international',
        store=True
    )
    
    # Détails financiers
    montant_frais = fields.Monetary(
        string='Montant des frais',
        compute='_compute_montant_frais',
        store=True,
        currency_field='currency_id',
        tracking=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Devise',
        default=lambda self: self.env.company.currency_id
    )
    
    # Mission
    mission_objet = fields.Text(
        string='Objet de la mission',
        required=True,
        tracking=True
    )
    
    ordre_mission_file = fields.Binary(
        string='Ordre de mission',
        required=True,
        attachment=True,
        help='Fichier PDF de l\'ordre de mission'
    )
    
    ordre_mission_filename = fields.Char(
        string='Nom du fichier'
    )
    
    # Workflow (Hiérarchie à 3 niveaux)
    state = fields.Selection([
        ('brouillon', 'Brouillon'),       # Employé crée
        ('soumis', 'Soumis'),             # Employé soumet
        ('approuve', 'Approuvé'),         # Manager valide (point unique de validation)
        ('en_cours', 'En cours'),         # DAF prend en charge
        ('termine', 'Terminé'),           # DAF termine
        ('refuse', 'Refusé'),             # Manager refuse
        ('annule', 'Annulé')              # Annulé
    ], string='État', default='brouillon', required=True, tracking=True)
    
    motif_refus = fields.Text(
        string='Motif de refus',
        tracking=True
    )
    
    # Champs techniques
    company_id = fields.Many2one(
        'res.company',
        string='Société',
        default=lambda self: self.env.company
    )
    
    active = fields.Boolean(
        string='Actif',
        default=True
    )
    
    # Compute methods
    @api.depends('employee_id')
    def _compute_manager_id(self):
        """Calcul automatique du manager de l'employé"""
        for record in self:
            if record.employee_id and record.employee_id.parent_id:
                record.manager_id = record.employee_id.parent_id
            else:
                record.manager_id = False
    
    @api.depends('date_debut', 'date_fin')
    def _compute_nb_jours(self):
        """Calcul du nombre de jours"""
        for record in self:
            if record.date_debut and record.date_fin:
                delta = record.date_fin - record.date_debut
                record.nb_jours = delta.days + 1 if delta.days >= 0 else 1
            else:
                record.nb_jours = 1
    
    @api.depends('destination_city_id', 'destination_city_id.country_id')
    def _compute_is_international(self):
        """Détermine si le déplacement est international (comparaison avec le pays de la société)"""
        company_country = self.env.company.country_id
        for record in self:
            if record.destination_city_id and record.destination_city_id.country_id and company_country:
                record.is_international = (record.destination_city_id.country_id.id != company_country.id)
            else:
                # Si pas de pays configuré sur la société, considérer comme national
                record.is_international = False
    
    @api.depends('nb_jours', 'is_international')
    def _compute_montant_frais(self):
        """Calcul automatique du montant des frais"""
        for record in self:
            if record.is_international:
                record.montant_frais = record.nb_jours * 1500.0
            else:
                record.montant_frais = record.nb_jours * 700.0
    
    @api.depends('distance_estimee', 'mode_transport')
    def _compute_classe_voyage(self):
        """Calcul de la classe de voyage pour l'avion"""
        for record in self:
            if record.mode_transport == 'avion':
                if record.distance_estimee > 6000:
                    record.classe_voyage = 'business'
                else:
                    record.classe_voyage = 'economique'
            else:
                record.classe_voyage = False
    
    # Constraints
    @api.constrains('date_debut', 'date_fin')
    def _check_dates(self):
        """Validation des dates"""
        for record in self:
            if record.date_debut and record.date_fin:
                if record.date_fin < record.date_debut:
                    raise ValidationError("La date de fin doit être supérieure ou égale à la date de début!")
    
    @api.constrains('distance_estimee')
    def _check_distance(self):
        """Validation de la distance"""
        for record in self:
            if record.distance_estimee <= 0:
                raise ValidationError("La distance doit être supérieure à 0!")
    
    @api.constrains('distance_estimee', 'mode_transport')
    def _check_transport_rules(self):
        """Validation des règles de transport"""
        for record in self:
            if record.mode_transport == 'avion' and record.distance_estimee < 500:
                raise ValidationError("L'avion n'est autorisé que pour les distances supérieures ou égales à 500 km.")
    
    @api.constrains('mode_transport', 'vehicule_id')
    def _check_vehicule(self):
        """Validation du véhicule de service"""
        for record in self:
            if record.mode_transport == 'vehicule_service' and not record.vehicule_id:
                raise ValidationError("Veuillez sélectionner un véhicule de service.")
            if record.mode_transport != 'vehicule_service' and record.vehicule_id:
                raise ValidationError("Le véhicule ne peut être sélectionné que si le mode de transport est 'Véhicule de service'.")
    
    @api.constrains('employee_id')
    def _check_employee_user(self):
        """Vérifier que l'employé correspond à l'utilisateur connecté (sauf pour les managers/admins)"""
        for record in self:
            # Permettre aux managers et admins de créer pour d'autres
            if self.env.user.has_group('gestionDeplacements.group_deplacement_manager'):
                continue
            if self.env.user.has_group('base.group_system'):
                continue
            # Pour les employés simples, vérifier la correspondance
            if record.employee_id.user_id and record.employee_id.user_id != self.env.user:
                raise ValidationError("Vous ne pouvez créer des demandes que pour vous-même!")
    
    # CRUD
    @api.model_create_multi
    def create(self, vals_list):
        """Génération automatique de la référence (fiable pour tous formats d'entrée)"""
        # Laisser Odoo gérer les formes d'entrée; créer d'abord les enregistrements
        records = super(DemandeDeplacement, self).create(vals_list)
        # Puis attribuer la séquence aux enregistrements encore à 'Nouveau'
        for rec in records:
            if rec.name == 'Nouveau':
                rec.name = self.env['ir.sequence'].next_by_code('gestion.deplacement.demande') or 'Nouveau'
        return records
    
    # Actions du workflow
    
    def action_submit(self):
        """[EMPLOYÉ] Soumettre la demande pour validation"""
        self.ensure_one()
        if not self.ordre_mission_file:
            raise ValidationError("Vous devez joindre l'ordre de mission avant de soumettre!")
        self.write({'state': 'soumis'})
        self.message_post(
            body="✅ Demande soumise pour validation par le manager",
            subtype_xmlid='mail.mt_comment'
        )
        
        # Activité pour le manager
        if self.manager_id and self.manager_id.user_id:
            # Ajouter le manager comme follower
            self.message_subscribe(partner_ids=[self.manager_id.user_id.partner_id.id])
            
            # Créer l'activité (notification principale)
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=self.manager_id.user_id.id,
                summary=f"Demande de déplacement à valider: {self.name}",
                note=f"L'employé {self.employee_id.name} a soumis une demande de déplacement."
            )
        
        # Email template (soumise)
        template = self.env.ref('gestionDeplacements.mail_template_demande_submitted', raise_if_not_found=False)
        if template:
            try:
                template.send_mail(self.id, force_send=True)
            except Exception as e:
                # Log l'erreur mais ne bloque pas le workflow
                self.message_post(body=f"⚠️ Erreur lors de l'envoi de l'email: {str(e)}")
    
    def action_approve(self):
        """[MANAGER] Approuver la demande"""
        self.ensure_one()
        self.write({'state': 'approuve', 'motif_refus': False})
        self.message_post(
            body="✅ Demande approuvée par le manager",
            subtype_xmlid='mail.mt_comment'
        )
        
        # Activités pour le DAF
        daf_group = self.env.ref('gestionDeplacements.group_deplacement_daf', raise_if_not_found=False)
        if daf_group:
            # Ajouter tous les DAF comme followers
            daf_partner_ids = [u.partner_id.id for u in daf_group.user_ids if u.partner_id]
            if daf_partner_ids:
                self.message_subscribe(partner_ids=daf_partner_ids)
            
            # Créer activité pour chaque DAF
            for user in daf_group.user_ids:
                self.activity_schedule(
                    'mail.mail_activity_data_todo',
                    user_id=user.id,
                    summary=f"Demande approuvée à traiter: {self.name}",
                    note=f"La demande de {self.employee_id.name} a été approuvée et nécessite un traitement."
                )
        
        # Email à l'employé (notification d'approbation)
        template_employee = self.env.ref('gestionDeplacements.mail_template_demande_approved', raise_if_not_found=False)
        if template_employee:
            try:
                template_employee.send_mail(self.id, force_send=True)
            except Exception as e:
                self.message_post(body=f"⚠️ Erreur lors de l'envoi de l'email à l'employé: {str(e)}")
        
        # Email au DAF (demande à traiter)
        template_daf = self.env.ref('gestionDeplacements.mail_template_demande_approved_daf', raise_if_not_found=False)
        if template_daf and daf_group:
            for user in daf_group.user_ids:
                if user.partner_id and user.partner_id.email:
                    try:
                        template_daf.with_context(partner_to=user.partner_id.id).send_mail(self.id, force_send=True, email_values={'recipient_ids': [(4, user.partner_id.id)]})
                    except Exception as e:
                        self.message_post(body=f"⚠️ Erreur lors de l'envoi de l'email au DAF: {str(e)}")

    
    def action_refuse(self):
        """[MANAGER] Ouvrir le wizard pour saisir le motif de refus"""
        self.ensure_one()
        return {
            'name': 'Refuser la demande',
            'type': 'ir.actions.act_window',
            'res_model': 'gestion.deplacement.demande.refus.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_demande_id': self.id,
            }
        }
    
    def action_process(self):
        """[DAF] Prendre en charge la demande"""
        self.ensure_one()
        self.write({'state': 'en_cours'})
        self.message_post(
            body="🔄 Demande prise en charge par le DAF",
            subtype_xmlid='mail.mt_comment'
        )
    
    def action_complete(self):
        """[DAF] Terminer le traitement"""
        self.ensure_one()
        self.write({'state': 'termine'})
        self.message_post(
            body="✅ Traitement terminé par le DAF",
            subtype_xmlid='mail.mt_comment'
        )
    
    def action_cancel(self):
        """[EMPLOYÉ/DAF] Annuler la demande"""
        self.ensure_one()
        self.write({'state': 'annule'})
        self.message_post(
            body="❌ Demande annulée",
            subtype_xmlid='mail.mt_comment'
        )
    
    def action_reset_draft(self):
        """[EMPLOYÉ] Remettre en brouillon (uniquement si refusée)"""
        self.ensure_one()
        if self.state != 'refuse':
            raise ValidationError("Seules les demandes refusées peuvent être remises en brouillon!")
        self.write({'state': 'brouillon', 'motif_refus': False})
        self.message_post(
            body="🔄 Demande remise en brouillon",
            subtype_xmlid='mail.mt_comment'
        )
