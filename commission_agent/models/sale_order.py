# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _inherit = "sale.order"

    commission_date = fields.Date(string="Commission date", compute="_compute_commission_date", store=True)

    def _get_last_day_month(self, date):
        last_day_of_month = date + relativedelta(day=31)

        return last_day_of_month

    @api.depends('date_order')
    def _compute_commission_date(self):
        """ Compute commission date """
        for order in self:
            commission_date = False
            if order.date_order:
                commission_date = self._get_last_day_month(order.date_order)

            order.commission_date = commission_date