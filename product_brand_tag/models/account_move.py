# -*- coding: utf-8 -*-
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super().action_post()

        for rec in self:
            # Filter invoice lines with a non-empty 'woo_brand_id'
            move_lines = rec.invoice_line_ids.filtered(lambda line: line.product_id.woo_brand_id)

            # Determine the target contact: parent_id if it exists, otherwise partner_id
            target_partner = rec.partner_id.parent_id or rec.partner_id

            # Add brands (woo_brand_id) as tags
            target_partner.brand_tag_ids = [
                Command.link(tag.id) for tag in move_lines.mapped('product_id.woo_brand_id')
            ]
        return res
