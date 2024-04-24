# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_reminder_line = fields.One2many(
        'payment.reminder.line',
        'move_id',
        string="Payment reminder",
        copy=False,
        readonly=False
    )
