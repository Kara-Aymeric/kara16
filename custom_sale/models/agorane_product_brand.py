# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AgoraneProductBrand(models.Model):
    _name = 'agorane.product.brand'
    _description = "Product brand of the Agorane company"

    name = fields.Char(
        string="Name"
    )
    description = fields.Char(
        string="Description"
    )
    active = fields.Boolean(
        default=True,
        help="By unchecking the active field, you can hide a product brand without deleting it."
    )
