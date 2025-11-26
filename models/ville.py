# -*- coding: utf-8 -*-

from odoo import models, fields


class Ville(models.Model):
    _name = 'gestion.deplacement.ville'
    _description = 'Ville'
    _order = 'name'

    name = fields.Char(
        string='Nom de la ville',
        required=True,
        index=True
    )
    
    country_id = fields.Many2one(
        'res.country',
        string='Pays',
        required=True,
        ondelete='restrict'
    )
    
    code_postal = fields.Char(
        string='Code postal'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    _sql_constraints = [
        ('name_country_unique', 'unique(name, country_id)', 'Cette ville existe déjà dans ce pays!')
    ]
    
    def name_get(self):
        """Affichage personnalisé: Ville, Pays"""
        result = []
        for ville in self:
            country_name = ville.country_id.name 
            name = f"{ville.name}, {country_name}" if country_name else ville.name
            result.append((ville.id, name))
        return result
