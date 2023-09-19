# -*- coding: utf-8 -*-
from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _update_partner_categories(self):
        """ Change partner tag when first invoice posted """
        partner_id = self.env['res.partner'].search([('id', '=', self.partner_id.id)])
        for partner_category_id in partner_id.category_id:
            # Search if label to replace
            replacement_category_ids = self.env['res.partner.category'].search([
                ('replace_after_invoice_category_id', '=', partner_category_id.id)]
            )
            if replacement_category_ids:
                # Replace label
                partner_id.write({'category_id': [(3, partner_category_id.id)]})
                for replacement_category_id in replacement_category_ids:
                    partner_id.write({'category_id': [(4, replacement_category_id.id)]})

    def action_post(self):
        """ Surcharge default function """
        res = super(AccountMove, self).action_post()
        self._update_partner_categories()

        return res
