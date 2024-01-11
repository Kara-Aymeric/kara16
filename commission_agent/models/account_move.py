# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class AccountMove(models.Model):
    _inherit = 'account.move'

    commission_date = fields.Date(string="Commission date", compute="_compute_commission_date", store=True)

    def _get_last_day_month(self, date):
        last_day_of_month = date + relativedelta(day=31)

        return last_day_of_month

    @api.depends('invoice_date')
    def _compute_commission_date(self):
        """ Compute commission date """
        for move in self:
            commission_date = False
            if move.invoice_date:
                commission_date = self._get_last_day_month(move.invoice_date)

            move.commission_date = commission_date
