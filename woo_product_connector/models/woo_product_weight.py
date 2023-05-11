# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class WooProductWeight(models.Model):
    _name = 'woo.product.weight'
    _description = "WooCommerce product weight"

    name = fields.Char(
        string="Name"
    )
    active = fields.Boolean(
        default=True,
        help="By unchecking the active field, you can hide a weight without deleting it."
    )