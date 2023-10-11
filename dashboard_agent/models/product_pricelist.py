# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    used_default_agent = fields.Boolean(string="Used by default for agent")
