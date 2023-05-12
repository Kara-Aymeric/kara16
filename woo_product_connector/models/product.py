# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    woo_name = fields.Char(
        string="Name",
        compute="_compute_woo_name",
        store=True,
        readonly=False,
        tracking=True
    )
    woo_list_price = fields.Monetary(
        string="Price (HT)",
        compute="_compute_woo_list_price",
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
    woo_sync = fields.Boolean(
        string="E-Shop synchro",
        help="When this option is active, the product is displayed on the e-commerce site. "
             "The unit price must be different from 0.",
        tracking=True
    )

    @api.depends('name')
    def _compute_woo_name(self):
        """ Get principal product template name """
        for product in self:
            woo_name = product.woo_name
            if product.name and not woo_name:
                woo_name = product.name

            product.woo_name = woo_name

    @api.depends('taxes_id')
    def _compute_woo_taxes_ids(self):
        """ Get principal taxes """
        for product in self:
            woo_taxes_ids = False
            if product.taxes_id:
                woo_taxes_ids = product.taxes_id

            product.woo_taxes_ids = woo_taxes_ids

    @api.depends('list_price')
    def _compute_woo_list_price(self):
        """ Get principal price unit """
        for product in self:
            woo_list_price = product.woo_list_price
            if product.list_price and woo_list_price == 0:
                woo_list_price = product.list_price

            product.woo_list_price = woo_list_price

    @api.depends('categ_id')
    def _compute_woo_categ_id(self):
        """ Get principal product category """
        for product in self:
            woo_categ_id = product.woo_categ_id
            if product.categ_id and not woo_categ_id:
                woo_categ_id = product.categ_id

            product.woo_categ_id = woo_categ_id

    @api.onchange('woo_categ_id')
    def _onchange_woo_categ_id(self):
        """ Allows to delete the value of the 'subcategory' field when the category is modified """
        self.woo_subcateg_id = False


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
    woo_product_subcateg_id = fields.Many2one(
        'product.category',
        string="Subcategory",
        compute="_compute_woo_product_subcateg_id",
        store=True,
        readonly=False,
        domain="[('parent_id', '=', woo_categ_id)]",
        help="This information is useful for the filters of the e-commerce site.",
        tracking=True
    )
    woo_product_weight_ids = fields.Many2many(
        'woo.product.weight',
        string="Weight",
        compute="_compute_woo_product_weight_ids",
        store=True,
        readonly=False,
        help="This information is the variants displayed on the product sheet of the e-commerce site.",
        tracking=True
    )
    woo_product_packing_ids = fields.Many2many(
        'woo.product.packing',
        string="Packing",
        compute="_compute_woo_product_packing_ids",
        store=True,
        readonly=False,
        help="This information is the variants displayed on the product sheet of the e-commerce site.",
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
            woo_product_name = product.woo_product_name
            if product.name and not woo_product_name:
                woo_product_name = product.name

            product.woo_product_name = woo_product_name

    @api.depends('lst_price')
    def _compute_woo_lst_price(self):
        """ Get principal price unit """
        for product in self:
            woo_lst_price = product.woo_lst_price
            if product.lst_price and woo_lst_price == 0:
                woo_lst_price = product.lst_price

            product.woo_lst_price = woo_lst_price

    @api.depends('woo_subcateg_id')
    def _compute_woo_product_subcateg_id(self):
        """ Get principal subcategory """
        for product in self:
            woo_product_subcateg_id = product.woo_product_subcateg_id
            if product.woo_subcateg_id and not woo_product_subcateg_id:
                woo_product_subcateg_id = product.woo_subcateg_id

            product.woo_product_subcateg_id = woo_product_subcateg_id

    @api.depends('woo_weight_ids')
    def _compute_woo_product_weight_ids(self):
        """ Get principal weight """
        for product in self:
            woo_product_weight_ids = product.woo_product_weight_ids
            if product.woo_weight_ids and not woo_product_weight_ids:
                woo_product_weight_ids = product.woo_weight_ids

            product.woo_product_weight_ids = woo_product_weight_ids

    @api.depends('woo_packing_ids')
    def _compute_woo_product_packing_ids(self):
        """ Get principal packing """
        for product in self:
            woo_product_packing_ids = product.woo_product_packing_ids
            if product.woo_packing_ids and not woo_product_packing_ids:
                woo_product_packing_ids = product.woo_packing_ids

            product.woo_product_packing_ids = woo_product_packing_ids

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

    @api.constrains('woo_product_sync', 'woo_lst_price')
    def _check_product_price_for_woo(self):
        """ Validation constraint if the price is zero when you want to synchronize the product with WooCommerce """
        for product in self:
            if product.woo_product_sync and product.woo_lst_price <= 0:
                raise ValidationError(
                    _("Invalid price. You cannot synchronize this product with the E-Shop. Please, enter a price.")
                )

    @api.onchange('woo_categ_id')
    def _onchange_woo_categ_id(self):
        """ Allows to delete the value of the 'subcategory' field when the category is modified """
        self.woo_subcateg_id = False
