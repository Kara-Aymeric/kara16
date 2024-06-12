# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    credit_customer_ids = fields.One2many(
        'credit.customer',
        'partner_id',
        string="Credits customer"
    )
