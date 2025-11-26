# -*- coding: utf-8 -*-

from odoo import models, fields


class ServiceVehicule(models.Model):
    _name = 'gestion.deplacement.service.vehicule'
    _description = 'Véhicules de service de l\'entreprise'
    _order = 'name'

    name = fields.Char(string='Nom du véhicule', required=True)
    immatriculation = fields.Char(string='Immatriculation')
    marque = fields.Char(string='Marque')
    modele = fields.Char(string='Modèle')
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company)
    active = fields.Boolean(default=True)
