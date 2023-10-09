# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountTax(models.Model):
    _inherit = 'account.tax'

    commission_tax = fields.Boolean(
        string="Tax for commission",
        copy=False,
        help="Allows you to generate this tax when the supplier does not reside in France"
    )
