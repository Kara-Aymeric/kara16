# -*- coding: utf-8 -*-
from odoo import fields, models


class PartnerFinancier(models.Model):
    _name = "partner.financier"
    _rec_name = "partner_id"
    _description = "Partner Financier"

    partner_id = fields.Many2one(
        'res.partner',
        string="Financier",
        required=True
    )
    description = fields.Char(
        string="Description"
    )
    add_auto_partner = fields.Boolean(
        string="Add auto on partner",
        help="Add automatic when partner create"
    )
    product_id = fields.Many2one(
        'product.template',
        string="Management fees product",
        required=True
    )
    active = fields.Boolean(
        default=True,
        help="By unchecking the active field, you can hide a record without deleting it."
    )
