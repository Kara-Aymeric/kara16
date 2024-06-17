# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError



class SaleOrder(models.Model):
    _inherit = "sale.order"

    remaining_credit = fields.Monetary(
        string="Remaining credit",
        compute="_compute_remaining_credit",
        store=True
    )

    show_credit = fields.Boolean(
        string="Show credit",
        compute="_compute_show_credit"
    )

    @api.depends(
        'partner_id',
        'partner_id.credit_customer_ids.remaining_credit',
        'payment_term_id',
        'payment_term_id.partner_funding'
    )
    def _compute_remaining_credit(self):
        """ Compute remaining credit for show """
        for order in self:
            remaining_credit = 0.0
            if order.partner_id and order.payment_term_id:
                if order.payment_term_id.partner_funding and order.payment_term_id.partner_financier_id:
                    credit_customer_id = self.env['credit.customer'].search(
                        [('partner_id', '=', order.partner_id.id),
                         ('partner_financier_id', '=', order.payment_term_id.partner_financier_id.id),
                         ('eligibility', '=', True)]
                    )
                    if credit_customer_id:
                        remaining_credit = credit_customer_id.remaining_credit

            order.remaining_credit = remaining_credit

    @api.depends('remaining_credit')
    def _compute_show_credit(self):
        """ Show banner into sale.order """
        for order in self:
            show_credit = False
            if order.remaining_credit > 0:
                show_credit = True

            order.show_credit = show_credit

    @api.constrains('state')
    def _constrains_state_confirm_order(self):
        """ Allows to control if remaining credit is more than total amount order """
        for order in self:
            if order.state not in ("draft", "cancel"):
                if order.remaining_credit < order.amount_total:
                    raise UserError(
                        _("The remaining credit is more than total amount order, "
                          "please change the payment terms or wait for the credit to be released")
                    )
