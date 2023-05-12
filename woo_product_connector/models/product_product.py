# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    woo_product_name = fields.Char(
        string="Name",
        compute="_compute_woo_product_name",
        store=True,
        readonly=False,
        tracking=True
    )
    woo_lst_price = fields.Monetary(
        string="Price (HT)",
        compute="_compute_woo_lst_price",
        store=True,
        readonly=False,
        tracking=True
    )
    woo_reference = fields.Char(
        string="Reference",
        compute="_compute_woo_reference",
        store=True,
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
    woo_product_sync = fields.Boolean(
        string="E-Shop variant synchro",
        help="When this option is active, the product is displayed on the e-commerce site. "
             "The unit price must be different from 0.",
        tracking=True
    )

    @api.depends('name')
    def _compute_woo_product_name(self):
        """ Get principal product name """
        for product in self:
            woo_product_name = False
            if product.name:
                woo_product_name = product.name

            product.woo_product_name = woo_product_name

    @api.depends('lst_price')
    def _compute_woo_lst_price(self):
        """ Get principal price unit """
        for product in self:
            woo_lst_price = False
            if product.lst_price:
                woo_lst_price = product.lst_price

            product.woo_lst_price = woo_lst_price

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
