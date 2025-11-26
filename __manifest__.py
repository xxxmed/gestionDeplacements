# -*- coding: utf-8 -*-
{
    'name': 'Gestion des Déplacements',
    'version': '1.0.0',
    'category': 'Operations',
    'summary': 'Module de gestion des déplacements et missions',
    'description': """
        Gestion des Déplacements
        =========================
        Ce module permet de gérer :
        * Les demandes de déplacement
        * Les missions
        * Le suivi des frais de déplacement
    """,
    'author': 'Ahmed Raji',
    'website': 'https://www.linkedin.com/in/ahmed-raji-2063a9237/',
    'depends': ['base', 'mail', 'hr'],
    'data': [
        # Security
        'security/deplacement_security.xml',
        
        # Data
        'data/sequence.xml',
        'data/ville_data.xml',
        'data/service_vehicule_data.xml',
        'data/email_templates.xml',
        
        # Views (chargées avant ir.model.access.csv pour créer les external IDs des modèles)
        'views/ville_view.xml',
        'views/demande_deplacement_view.xml',
        'views/service_vehicule_view.xml',
        'views/menu.xml',
        
        # Wizards
        'wizard/demande_refus_wizard_view.xml',
        
        # Security - Access rights (doit être chargé après les vues)
        'security/ir.model.access.csv',
    ],
    'demo': [
        # Demo data
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
