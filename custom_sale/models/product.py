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

    @api.model
    def _get_supplier_id_domain(self):
        """ Allows you to search only for contacts with the supplier label """
        domain = []
        category_supplier = self.env.ref('custom_sale.kara_res_partner_category_supplier', False)
        if category_supplier:
            domain = [('category_id.id', '=', category_supplier.id)]
        return domain

    access_packing = fields.Boolean(string="Access packing", related="company_id.access_packing")
    product_brand = fields.Char(string="Brand", tracking=True)
    supplier_id = fields.Many2one(
        'res.partner', string="Supplier", help="Industrial or warehouse", domain=_get_supplier_id_domain, tracking=True
    )
    packing_ids = fields.One2many('product.packing', 'product_template_id', string='Packing')
    ingredient = fields.Char(string="Ingredient")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_ingredient = fields.Char(
        string="Ingredient",
        compute="_compute_product_ingredient",
        store=True,
        readonly=False,
        tracking=True
    )

    @api.depends('ingredient')
    def _compute_product_ingredient(self):
        """ Get principal ingredient """
        for product in self:
            product_ingredient = product.product_ingredient
            if product.ingredient and not product_ingredient:
                product_ingredient = product.ingredient

            product.product_ingredient = product_ingredient


class ProductPacking(models.Model):
    _name = 'product.packing'

    name = fields.Selection(
        [('article', 'Article'), ('box', 'Box'), ('pallet', 'Pallet')], string="Type"
    )
    qty = fields.Integer(string="Quantity")
    packing_uom = fields.Many2one('uom.uom', string="Unit of measurement")
    product_template_id = fields.Many2one('product.template', string="Product template")
