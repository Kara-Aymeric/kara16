# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    dashboard_product_commission = fields.Monetary(string="Commission")
    dashboard_price_commission = fields.Monetary(string="Total commission")

    def _change_dashboard_price_commission(self, commission, qty):
        """ Total commission line calculation """
        self.write({
            'dashboard_product_commission': commission,
            'dashboard_price_commission': qty * commission,
        })

    @api.onchange('price_unit')
    def _onchange_price_unit(self):
        """ Si price unit is updated in order line and if commission is percentage type, recalculate commission line """
        product_tmpl_id = self.product_template_id
        qty = self.product_uom_qty
        percentage_value = 0.0
        for agent in product_tmpl_id.agent_commission_ids:
            if self.order_id.user_id == agent.user_id:
                percentage_value = agent.percentage_value

        sale_commission = (percentage_value / 100) * self.price_unit
        self._change_dashboard_price_commission(sale_commission, qty)
    #
    # @api.onchange('product_id', 'product_uom_qty')
    # def _onchange_product_id_uom_qty(self):
    #     """ Get principal commission product """
    #     sale_commission = self.product_template_id.sale_commission
    #     qty = self.product_uom_qty
    #     if sale_commission > 0:
    #         self._change_price_commission(sale_commission, qty)
    #
    # @api.onchange('product_commission')
    # def _onchange_product_commission(self):
    #     """ Change manually commission """
    #     sale_commission = self.product_commission
    #     qty = self.product_uom_qty
    #     if sale_commission > 0:
    #         self._change_price_commission(sale_commission, qty)
