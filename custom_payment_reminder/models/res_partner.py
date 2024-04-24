# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    no_payment_reminder = fields.Boolean(
        string="No payment reminder",
        tracking=True,
        copy=False,
        help="By activating this feature, you deactivate payment reminders for this contact",
    )

    payment_reminder_history_ids = fields.One2many(
        "payment.reminder.history",
        "partner_id",
        copy=False
    )

