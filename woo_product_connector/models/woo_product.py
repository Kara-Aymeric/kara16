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