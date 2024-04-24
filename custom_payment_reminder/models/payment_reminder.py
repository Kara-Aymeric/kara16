# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class PaymentReminder(models.Model):
    _name = "payment.reminder"
    _description = "Payment Reminder"

    name = fields.Char(
        string="Name",
        readonly=True,
    )

    days = fields.Integer(
        string="Days",
        help="You can enter a positive or negative value here",
    )

    mail_template_id = fields.Many2one(
        "mail.template",
        string="Mail Template",
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
        index=True,
    )

    active = fields.Boolean(
        default=True,
        help="By unchecking the active field, you can hide a record without deleting it."
    )
