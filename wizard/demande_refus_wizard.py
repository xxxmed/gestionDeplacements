# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class DemandeRefusWizard(models.TransientModel):
    _name = 'gestion.deplacement.demande.refus.wizard'
    _description = 'Assistant de refus de demande'

    motif_refus = fields.Text(
        string="Motif de refus",
        required=True,
        help="Indiquez la raison pour laquelle vous refusez cette demande"
    )
    
    demande_id = fields.Many2one(
        'gestion.deplacement.demande',
        string="Demande",
        required=True,
        ondelete='cascade'
    )

    def action_confirm_refus(self):
        """Confirmer le refus avec le motif saisi"""
        self.ensure_one()
        if not self.motif_refus:
            raise ValidationError("Le motif de refus est obligatoire!")
        
        # Appliquer le refus sur la demande
        self.demande_id.write({
            'state': 'refuse',
            'motif_refus': self.motif_refus
        })
        
        # Message dans le chatter
        self.demande_id.message_post(
            body=f"❌ Demande refusée par le manager. Motif: {self.motif_refus}",
            subtype_xmlid='mail.mt_comment'
        )
        
        # Envoyer l'email de refus
        template = self.env.ref('gestionDeplacements.mail_template_demande_refused', raise_if_not_found=False)
        if template:
            try:
                template.send_mail(self.demande_id.id, force_send=True)
            except Exception as e:
                # Log l'erreur mais ne bloque pas le workflow
                self.demande_id.message_post(body=f"⚠️ Erreur lors de l'envoi de l'email: {str(e)}")
        
        return {'type': 'ir.actions.act_window_close'}
