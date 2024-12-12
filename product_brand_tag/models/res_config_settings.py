# -*- coding: utf-8 -*-
from odoo import models, Command


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def assign_brand_tags(self):
        """ Assign brand tags into contact profiles. """
        move_lines = self.env['account.move.line'].sudo().search([
            ('product_id.woo_brand_id', '!=', False),
            ('parent_state', '=', 'posted')
        ])

        # Mapping partners with product brands associated
        for line in move_lines:
            if line.partner_id and line.product_id.woo_brand_id:
                # Assign tag into partner profile
                line.partner_id.write({
                    'brand_tag_ids': [Command.link(line.product_id.woo_brand_id.id)]
                })
