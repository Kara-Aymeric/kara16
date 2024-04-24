# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PaymentReminderLine(models.Model):
    _name = "payment.reminder.line"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "Payment Reminder Line"
    _order = "id desc"

    move_id = fields.Many2one(
        'account.move',
        string="Move",
        readonly=True,
        store=True,
        copy=False,
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Partner",
        related="move_id.partner_id",
        store=True,
        copy=False,
    )

    invoice_date = fields.Date(
        string="Invoice date",
        related="move_id.invoice_date",
        store=True,
        copy=False,
    )

    invoice_origin = fields.Char(
        string="Origin",
        related="move_id.invoice_origin",
        copy=False,
    )

    payment_reminder_id = fields.Many2one(
        'payment.reminder',
        string="Payment reminder",
        required=True,
        store=True,
        copy=False,
    )

    date_maturity = fields.Date(
        string='Due Date',
        copy=False,
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related="move_id.currency_id",
        store=True,
        copy=False,
    )

    amount_residual = fields.Monetary(
        string='Amount Due',
        related="move_id.amount_residual",
        store=True,
        copy=False,
    )


