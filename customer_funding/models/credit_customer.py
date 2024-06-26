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
        compute="_compute_invoice_ids",
        store=True,
        help="Target invoices for calcul credit"
    )

    @api.depends(
        'partner_id',
        'partner_id.child_ids',
        'partner_id.invoice_ids.state',
        'partner_id.child_ids.invoice_ids.state',
        'partner_financier_id',
        'eligibility'
    )
    def _compute_invoice_ids(self):
        """ Compute invoices """
        for credit in self:
            invoice_ids = False
            if credit.partner_id and credit.partner_financier_id and credit.eligibility:
                # Get all payment terms to financier and deferred payment
                payment_terms_ids = self.env['account.payment.term'].search([
                    ('partner_financier_id', '=', credit.partner_financier_id.id), ('deferred_payment', '=', True)]
                )

                # Get all invoices associated payment terms deferred
                all_invoices = []

                # For partner
                partner_invoice_ids = self.partner_id.invoice_ids.filtered(
                    lambda x: x.invoice_payment_term_id in payment_terms_ids and x.state == "posted"
                )
                all_invoices += partner_invoice_ids.ids

                # For child_ids partner
                for child in credit.partner_id.child_ids:
                    child_invoice_ids = child.invoice_ids.filtered(
                        lambda x: x.invoice_payment_term_id in payment_terms_ids and x.state == "posted"
                    )
                    all_invoices += child_invoice_ids.ids

                invoice_ids = [(6, 0, all_invoices)]

            credit.invoice_ids = invoice_ids

    @api.depends('eligibility', 'invoice_ids', 'invoice_ids.amount_residual')
    def _compute_current_credit(self):
        """ Get total amount residual """
        for credit in self:
            current_credit = 0
            if credit.eligibility:
                for invoice in credit.invoice_ids:
                    current_credit += invoice.amount_residual

            credit.current_credit = current_credit

    @api.depends('base_credit', 'current_credit')
    def _compute_remaining_credit(self):
        """ Get remaining credit """
        for credit in self:
            credit.remaining_credit = credit.base_credit - credit.current_credit

    def action_view_invoices(self):
        """ View invoices """
        self.ensure_one()
        invoices = self.invoice_ids
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_out_invoice_type')
        action['domain'] = [('id', 'in', invoices.ids)]

        return action
