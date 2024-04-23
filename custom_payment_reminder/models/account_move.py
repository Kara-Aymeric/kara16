# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    partner_payment_reminder_line = fields.One2many(
        'partner.payment.reminder.line',
        'move_id',
        string="Payment reminder",
        copy=False,
        readonly=False
    )
