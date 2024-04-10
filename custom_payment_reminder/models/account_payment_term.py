# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

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
