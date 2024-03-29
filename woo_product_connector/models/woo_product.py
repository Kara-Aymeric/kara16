# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from random import randint


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
        string="Name",
        compute="_compute_name",
        store=True
    )
    quantity = fields.Integer(
        string="Quantity"
    )
    weight_uom = fields.Many2one(
        'uom.uom',
        string="Unit of measurement"
    )
    active = fields.Boolean(
        default=True,
        help="By unchecking the active field, you can hide a weight without deleting it."
    )

    @api.depends('quantity', 'weight_uom')
    def _compute_name(self):
        """ Compute name """
        for record in self:
            name = ""
            if record.quantity and record.weight_uom:
                name = f"{record.quantity}{record.weight_uom.name}"

            record.name = name


class WooProductStatus(models.Model):
    _name = 'woo.product.status'
    _description = "WooCommerce product status"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(
        string="Name"
    )
    color = fields.Integer(
        string="Color",
        default=_get_default_color
    )
    discount_status = fields.Boolean(
        string="Discount status",
        help="Enable this option if the status is part of a promotional status. Useful for WooCommerce."
    )

    active = fields.Boolean(
        default=True,
        help="By unchecking the active field, you can hide a brand without deleting it."
    )
