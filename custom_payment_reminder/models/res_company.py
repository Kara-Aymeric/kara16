# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    is_payment_reminder = fields.Boolean(
        string="Active payment reminder",
        help="Allows you to activate the payment reminder for this company",
        tracking=True,
        copy=False
    )
