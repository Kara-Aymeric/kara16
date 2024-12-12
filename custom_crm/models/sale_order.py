# -*- coding: utf-8 -*-
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    partner_typology_id = fields.Many2one(
        'partner.typology', string="Typology",
        store=True, related="partner_id.partner_typology_id"
    )

    partner_typology_id2 = fields.Many2one(
        'partner.typology', string="Specificity",
        store=True, related="partner_id.partner_typology_id2"
    )
