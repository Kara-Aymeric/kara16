# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_reminder_ids = fields.One2many(
        'account.move.line',
        compute='_compute_payment_reminder_ids',
        readonly=False
    )

    def _get_payment_reminder_domain(self):
        return [
            ('reconciled', '=', False),
            ('account_id.deprecated', '=', False),
            ('account_id.account_type', '=', 'asset_receivable'),
            ('parent_state', '=', 'posted'),
            ('partner_id', '=', self.partner_id.id),
            ('company_id', '=', self.env.company.id),
        ]

    @api.depends('partner_id')
    def _compute_payment_reminder_ids(self):
        """ """
        values = {
            read['partner_id'][0]: read['line_ids']
            for read in self.env['account.move.line'].read_group(
                domain=self._get_payment_reminder_domain(),
                fields=['line_ids:array_agg(id)'],
                groupby=['partner_id']
            )
        }
        for move in self:
            move.payment_reminder_ids = values.get(move.partner_id.id, False)
