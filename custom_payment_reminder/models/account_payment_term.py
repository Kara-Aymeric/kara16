# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    payment_reminder_id1 = fields.Many2one(
        'payment.reminder',
        string="Payment reminder 1",
        help="If a value is entered, the chosen payment reminder will be active. "
             "So be sure to configure your reminder email correctly.",
        copy=False,
        store=True
    )

    payment_reminder_id2 = fields.Many2one(
        'payment.reminder',
        string="Payment reminder 2",
        help="If a value is entered, the chosen payment reminder will be active. "
             "So be sure to configure your reminder email correctly.",
        copy=False,
        store=True
    )

    payment_reminder_id3 = fields.Many2one(
        'payment.reminder',
        string="Payment reminder 3",
        help="If a value is entered, the chosen payment reminder will be active. "
             "So be sure to configure your reminder email correctly.",
        copy=False,
        store=True
    )

    email_subject_x1 = fields.Char(
        string="Subject X1",
        help="Dynamic data (example: #clientname)",
        copy=False,
        store=True,
        translate=True
    )

    email_subject_x2 = fields.Char(
        string="Subject X2",
        help="Dynamic data (example: #clientname)",
        copy=False,
        store=True,
        translate=True
    )

    email_subject_x3 = fields.Char(
        string="Subject X3",
        help="Dynamic data (example: #clientname)",
        copy=False,
        store=True,
        translate=True
    )

    email_content_x1 = fields.Html(
        string="Content X1",
        help="Dynamic data (example: #clientname)",
        copy=False,
        store=True,
        translate=True
    )

    email_content_x2 = fields.Html(
        string="Content X2",
        help="Dynamic data (example: #clientname)",
        copy=False,
        store=True,
        translate=True
    )

    email_content_x3 = fields.Html(
        string="Content X3",
        help="Dynamic data (example: #clientname)",
        copy=False,
        store=True,
        translate=True
    )
