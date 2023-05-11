# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class WooProductPacking(models.Model):
    _name = 'woo.product.packing'
    _description = "WooCommerce product packing"

    name = fields.Char(
        string="Name"
    )
    active = fields.Boolean(
        default=True,
        help="By unchecking the active field, you can hide a packing without deleting it."
    )
