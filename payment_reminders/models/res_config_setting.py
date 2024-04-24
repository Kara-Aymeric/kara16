# -*- coding: utf-8 -*-
# © 2018-Today Aktiv Software (http://www.aktivsoftware.com).
# Part of AktivSoftware See LICENSE file for full copyright
# and licensing details.
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    is_payment_reminder = fields.Boolean(
        related="company_id.is_payment_reminder",
        string="Enable Payment Reminder",
        readonly=False,
    )
