# -*- coding: utf-8 -*-
# © 2018-Today Aktiv Software (http://www.aktivsoftware.com).
# Part of AktivSoftware See LICENSE file for full copyright
# and licensing details.
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_payment_reminders_ids = fields.One2many(
        "payment.reminders.history",
        "partner_id",
    )
