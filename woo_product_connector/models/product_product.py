# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    woo_name = fields.Char(
        string="Name",
        tracking=True
    )
    woo_price = fields.Monetary(
        string="Price (HT)",
        compute="_compute_woo_price",
        store=True,
        readonly=False,
        tracking=True
    )
    woo_taxes_ids = fields.Many2many(
        comodel_name='account.tax',
        string="Taxes",
        domain=[('type_tax_use', '=', 'sale')],
        help="Taxes used for WooCommerce",
        compute="_compute_woo_taxes_ids",
        store=True,
        tracking=True
    )
    woo_brand_id = fields.Many2one(
        'woo.product.brand',
        string="Brand",
        tracking=True
    )
    woo_categ_id = fields.Many2one(
        'product.category',
        string="Category",
        help="This information is useful for the filters of the e-commerce site.",
        compute="_compute_woo_categ_id",
        store=True,
        readonly=False,
        tracking=True
    )
    woo_subcateg_id = fields.Many2one(
        'product.category',
        string="Subcategory",
        domain="[('parent_id', '=', woo_categ_id)]",
        help="This information is useful for the filters of the e-commerce site.",
        tracking=True
    )
    woo_reference = fields.Char(
        string="Reference",
        compute="_compute_woo_reference",
        store=True,
        tracking=True
    )
    woo_weight_ids = fields.Many2many(
        'woo.product.weight',
        string="Weight",
        help="This information is the variants displayed on the product sheet of the e-commerce site.",
        tracking=True
    )
    woo_packing_ids = fields.Many2many(
        'woo.product.packing',
        string="Packing",
        help="This information is the variants displayed on the product sheet of the e-commerce site.",
        tracking=True
    )
    woo_barcode = fields.Char(
        string="Barcode",
        compute="_compute_woo_barcode",
        store=True,
        tracking=True
    )
    woo_barcode_file = fields.Binary(
        string="Barcode (image)",
        tracking=True
    )
    woo_sync = fields.Boolean(
        string="E-Shop synchro",
        help="When this option is active, the product is displayed on the e-commerce site. "
             "The unit price must be different from 0.",
        tracking=True
    )

    @api.depends('taxes_id')
    def _compute_woo_taxes_ids(self):
        """ Get principal taxes """
        for product in self:
            woo_taxes_ids = False
            if product.taxes_id:
                woo_taxes_ids = product.taxes_id

            product.woo_taxes_ids = woo_taxes_ids

    @api.depends('lst_price')
    def _compute_woo_price(self):
        """ Get principal price unit """
        for product in self:
            woo_price = False
            if product.lst_price:
                woo_price = product.lst_price

            product.woo_price = woo_price

    @api.depends('categ_id')
    def _compute_woo_categ_id(self):
        """ Get principal product category """
        for product in self:
            woo_categ_id = False
            if product.categ_id:
                woo_categ_id = product.categ_id

            product.woo_categ_id = woo_categ_id

    @api.depends('default_code')
    def _compute_woo_reference(self):
        """ Get principal reference """
        for product in self:
            woo_reference = False
            if product.default_code:
                woo_reference = product.default_code

            product.woo_reference = woo_reference

    @api.depends('barcode')
    def _compute_woo_barcode(self):
        """ Get principal barcode """
        for product in self:
            woo_barcode = False
            if product.barcode:
                woo_barcode = product.barcode

            product.woo_barcode = woo_barcode

    @api.onchange('woo_categ_id')
    def _onchange_woo_categ_id(self):
        """ Allows to delete the value of the 'subcategory' field when the category is modified """
        self.woo_subcateg_id = False
