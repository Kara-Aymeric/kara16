# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    trading_business = fields.Boolean(string="Trading business",
                                      help="Allows you to have a different sales flow than the standard sales flow")
    access_packing = fields.Boolean(string="Allows the company to access the packing of articles")
