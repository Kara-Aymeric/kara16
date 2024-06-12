# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CreditCustomer(models.Model):
    _name = "credit.customer"
    _rec_name = "partner_financier_id"
    _description = "Partner Financier"

    partner_id = fields.Many2one(
        'res.partner',
        string="Partner"
    )
    partner_financier_id = fields.Many2one(
        'partner.financier',
        string="Financier"
    )
    eligibility = fields.Boolean(
        string="Eligibility"
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
        readonly=True
    )
    base_credit = fields.Monetary(
        string="Base credit"
    )
    date_update_base_credit = fields.Date(
        string="Date update base credit"
    )
    current_credit = fields.Monetary(
        string="Current credit",
        compute="_compute_current_credit",
        store=True
    )
    remaining_credit = fields.Monetary(
        string="Remaining credit",
        compute="_compute_remaining_credit",
        store=True
    )
    invoice_ids = fields.Many2many(
        'account.move',
        string="Invoices",
        help="Target invoices for calcul credit"
    )

    @api.depends('invoice_ids', 'invoice_ids.amount_paid')
    def _compute_current_credit(self):
        """ Get total amount payed """
        for credit in self:
            current_credit = 0
            for invoice in credit.invoice_ids:
                current_credit += invoice.amount_paid

            credit.current_credit = current_credit

    @api.depends('base_credit', 'current_credit')
    def _compute_remaining_credit(self):
        """ Get remaining credit """
        for credit in self:
            credit.remaining_credit = credit.base_credit - credit.current_credit
