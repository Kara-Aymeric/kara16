# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_commission = fields.Monetary(string="Commission")
    price_commission = fields.Monetary(string="Commission totale")

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_id_uom_qty(self):
        """ Get principal commission product and total commission line calculation """
        sale_commission = self.product_template_id.sale_commission
        qty = self.product_uom_qty
        if sale_commission > 0:
            self.write({
                'product_commission': sale_commission,
                'price_commission': qty * sale_commission,
            })
