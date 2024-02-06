# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    dashboard_product_commission = fields.Monetary(string="Commission")
    dashboard_price_commission = fields.Float(string="Total commission")
    restrict_custom_field = fields.Boolean(
        string="Restrict custom field", compute="_compute_restrict_custom_field"
    )

    @api.depends('order_id', 'order_id.restrict_custom_field')
    def _compute_restrict_custom_field(self):
        """ Compute readonly custom field """
        for record in self:
            restrict_custom_field = False
            if record.order_id:
                restrict_custom_field = record.order_id.restrict_custom_field

            record.restrict_custom_field = restrict_custom_field

    def _change_dashboard_price_commission(self, commission, qty):
        """ Total commission line calculation """
        self.write({
            'dashboard_product_commission': commission,
            'dashboard_price_commission': qty * commission,
        })

    def _get_commission_value(self):
        """ Get commission value into partner profile depending discount """
        if self.discount > 0:
            commission = self.order_id.agent_partner_id.agent_discount_commission
            if commission <= 0 and self.order_id.agent_partner_id.parent_id:
                commission = self.order_id.agent_partner_id.parent_id.agent_discount_commission
        else:
            commission = self.order_id.agent_partner_id.agent_commission
            if commission <= 0 and self.order_id.agent_partner_id.parent_id:
                commission = self.order_id.agent_partner_id.parent_id.agent_commission

        return commission

    @api.onchange('price_unit', 'product_id', 'product_uom_qty', 'discount')
    def _onchange_price_unit_product_id_product_uom_qty_discount(self):
        """ Si price unit is updated in order line recalculate commission line """
        qty = self.product_uom_qty
        sale_commission = (self._get_commission_value() / 100) * self.price_unit
        self._change_dashboard_price_commission(sale_commission, qty)

    @api.onchange('dashboard_product_commission')
    def _onchange_dashboard_product_commission(self):
        """ Change manually commission """
        sale_commission = self.dashboard_product_commission
        qty = self.product_uom_qty
        self._change_dashboard_price_commission(sale_commission, qty)
