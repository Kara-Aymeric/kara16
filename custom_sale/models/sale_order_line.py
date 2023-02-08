# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    packing_type = fields.Selection(
        [('box', 'Box'), ('pallet', 'Pallet')],
        string='Packing',  help="Packing type (pallet or box)", store=True,
        related="product_template_id.categ_id.packing_type"
    )
    product_brand = fields.Char(string="Brand", store=True, related="product_template_id.product_brand")

