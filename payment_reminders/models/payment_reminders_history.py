# -*- coding: utf-8 -*-
# © 2018-Today Aktiv Software (http://www.aktivsoftware.com).
# Part of AktivSoftware See LICENSE file for full copyright
# and licensing details.
from odoo import fields, models


class PaymentRemindersHistory(models.Model):
    _name = "payment.reminders.history"
    _description = "Payment Reminders History"

    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
    )
    invoice_id = fields.Many2one(
        "account.move",
        string="Invoice",
    )
    mail_date = fields.Date()
    due_date = fields.Date()
    email_template_id = fields.Many2one(
        "mail.template",
        string="Email Template",
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env["res.company"]._company_default_get(
            "payment.reminders.history"
        ),
        index=True,
        required=True,
    )
