# -*- coding: utf-8 -*-
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    brand_tag_ids = fields.Many2many('woo.product.brand', string="Brands")
