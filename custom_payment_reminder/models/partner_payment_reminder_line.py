# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PartnerPaymentReminderLine(models.Model):
    _name = "partner.payment.reminder.line"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "Partner Payment Reminder Line"
    _order = "id desc"

    move_id = fields.Many2one(
        'account.move',
        string="Move",
        readonly=True,
        store=True,
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Partner",
        related="move_id.partner_id",
        store=True,
    )

    invoice_date = fields.Date(
        string="Invoice date",
        related="move_id.invoice_date",
        store=True,
    )

    invoice_origin = fields.Char(
        string="Origin",
        related="move_id.invoice_origin"
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related="move_id.currency_id",
        store=True
    )

    amount_residual = fields.Monetary(
        string='Amount Due',
        related="move_id.amount_residual",
        store=True,
    )

    date_maturity = fields.Date(
        string='Due Date'
    )

