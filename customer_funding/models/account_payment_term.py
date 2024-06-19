# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"

    partner_funding = fields.Boolean(
        string="Partner funding",
    )

    deferred_payment = fields.Boolean(
        string="Deferred payment",
        help="This option is useful if you want to update the customer's credit",
    )

    partner_financier_id = fields.Many2one(
        'partner.financier',
        string="Financier"
    )

    management_fees = fields.Float(
        string="Management fees (%)"
    )

    fees_based_on = fields.Selection(
        [('total_amount_sale', 'Sale TTC'), ('total_amount_purchase', 'Purchase TTC')],
        string='Based on',
    )
