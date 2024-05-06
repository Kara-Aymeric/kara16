# -*- coding: utf-8 -*-
import re
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    no_payment_reminder = fields.Boolean(
        string="No payment reminder",
        compute="_compute_no_payment_reminder",
        readonly=False,
        required=True,
        store=True,
        copy=False,
        help="By activating this feature, you deactivate payment reminders for this contact",
    )

    payment_reminder_history_ids = fields.One2many(
        "payment.reminder.history",
        "partner_id",
        copy=False
    )

    @api.depends('parent_id', 'parent_id.no_payment_reminder')
    def _compute_no_payment_reminder(self):
        """ This value for this field would same for all relation partner """
        for partner in self:
            if partner.parent_id:
                no_payment_reminder = partner.parent_id.no_payment_reminder
                partner.no_payment_reminder = no_payment_reminder
                for child in partner.child_ids:
                    if partner.parent_id:
                        child.no_payment_reminder = no_payment_reminder
