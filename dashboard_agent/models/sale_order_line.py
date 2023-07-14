# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    dashboard_product_commission = fields.Monetary(string="Commission")
    dashboard_price_commission = fields.Monetary(string="Total commission")

