# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class WooProductBrand(models.Model):
    _name = 'woo.product.brand'
    _description = "WooCommerce product brand"

    name = fields.Char(
        string="Name"
    )
    active = fields.Boolean(
        default=True,
        help="By unchecking the active field, you can hide a brand without deleting it."
    )
