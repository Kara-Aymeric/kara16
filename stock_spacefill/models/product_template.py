#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""


:copyright: (c) 2022 irokoo
:license: AGPLv3, see LICENSE for more details


"""
from odoo import models, fields, api, exceptions, _
from odoo.addons.stock_spacefill.spacefillpy.api import API as API


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    is_products_exported = fields.Boolean('SpaceFill Product(s)', compute='_compute_is_products_exported',default=False)

    def _compute_is_products_exported(self):
        for product in self:
            product.is_products_exported = False
            for variant in product.product_variant_ids:
                if variant.is_exported:
                    product.is_products_exported = True
                    break


    def export_product_tmpl_in_spacefill(self):
        for product in self:
            for variant in product.product_variant_ids:
                variant.export_product_in_spacefill()

    def write(self, vals):
        res = super(ProductTemplate, self).write(vals)
        if 'active' not in vals:
            for product in self:
                    if product.is_products_exported:
                        for variant in product.product_variant_ids:
                            variant.export_product_in_spacefill()
        return res