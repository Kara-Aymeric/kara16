# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductCategory(models.Model):
    _inherit = 'product.category'

    packing_type = fields.Selection(
        [('box', 'Box'), ('pallet', 'Pallet')],
        string='Packing type',  help="Packing type (pallet or box)"
    )


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    access_packing = fields.Boolean(string="Trading business", related="company_id.access_packing")
    product_brand = fields.Char(string="Brand")
    supplier_id = fields.Many2one('res.partner', string="Supplier", help="Industrial or warehouse")
    packing_ids = fields.One2many('product.packing', 'product_template_id', string='Packing')


class ProductPacking(models.Model):
    _name = 'product.packing'

    name = fields.Selection(
        [('article', 'Article'), ('box', 'Box'), ('pallet', 'Pallet')], string="Type"
    )
    qty = fields.Integer(string="Quantity")
    packing_uom = fields.Many2one('uom.uom', string="Unit of measurement")
    product_template_id = fields.Many2one('product.template', string="Product template")
