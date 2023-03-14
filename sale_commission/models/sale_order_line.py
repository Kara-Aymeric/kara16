# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_commission = fields.Monetary(string="Commission")
    price_commission = fields.Monetary(string="Total commission")

    def _change_price_commission(self, commission, qty):
        """ Total commission line calculation """
        self.write({
            'product_commission': commission,
            'price_commission': qty * commission,
        })

    @api.onchange('price_unit')
    def _onchange_price_unit(self):
        """ Si price unit is updated in order line and if commission is percentage type, recalculate commission line """
        product_tmpl_id = self.product_template_id
        qty = self.product_uom_qty
        if product_tmpl_id.commission_type == 'percentage' and product_tmpl_id.percentage_value > 0:
            sale_commission = (product_tmpl_id.percentage_value / 100) * self.price_unit
            self._change_price_commission(sale_commission, qty)

    @api.onchange('product_id', 'product_uom_qty')
    def _onchange_product_id_uom_qty(self):
        """ Get principal commission product """
        sale_commission = self.product_template_id.sale_commission
        qty = self.product_uom_qty
        if sale_commission > 0:
            self._change_price_commission(sale_commission, qty)

    @api.onchange('product_commission')
    def _onchange_product_commission(self):
        """ Change manually commission """
        sale_commission = self.product_commission
        qty = self.product_uom_qty
        if sale_commission > 0:
            self._change_price_commission(sale_commission, qty)
