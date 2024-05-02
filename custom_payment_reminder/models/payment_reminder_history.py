# -*- coding: utf-8 -*-
from odoo import fields, models


class PaymentReminderHistory(models.Model):
    _name = "payment.reminder.history"
    _description = "Payment Reminder History"
    _order = "id desc"

    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
    )

    invoice_id = fields.Many2one(
        "account.move",
        string="Invoice",
    )

    mail_reminder_date = fields.Date(
        string="Mail reminder date",
        help="Date the reminder email was sent"
    )

    payment_reminder_line_id = fields.Many2one(
        "payment.reminder.line",
        string="Reminder detail"
    )
