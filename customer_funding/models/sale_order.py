# -*- coding: utf-8 -*-
from datetime import datetime
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
        compute="_compute_show_credit",
        store=True
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
                    domain = [
                        ('partner_financier_id', '=', order.payment_term_id.partner_financier_id.id),
                        ('eligibility', '=', True)
                    ]
                    if order.partner_id.parent_id:
                        domain += [('partner_id', '=', order.partner_id.parent_id.id)]
                    else:
                        domain += [('partner_id', '=', order.partner_id.id)]

                    credit_customer_id = self.env['credit.customer'].search(domain)
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
            if order.state not in ("draft", "cancel") and order.remaining_credit != 0:
                if order.remaining_credit < order.amount_total:
                    raise UserError(
                        _("The remaining credit is more than total amount order, "
                          "please change the payment terms or wait for the credit to be released")
                    )

    def create_purchase_invoice(self, financier_id):
        """ Create purchase """
        if financier_id:
            data = {
                'partner_id': financier_id.id,
                'move_type': "in_invoice",
                'invoice_date': datetime.today(),
            }
            purchase_invoice_id = self.env['account.move'].create(data)
            return purchase_invoice_id
        return False

    def calculation_price_unit_line(self, payment_term_id):
        """ Calculation price unit depending payment term config """
        if payment_term_id.partner_funding:
            based_on = payment_term_id.fees_based_on
            if based_on == "total_amount_sale":
                return self.amount_total * (payment_term_id.management_fees/100)

    def create_purchase_invoice_line(
            self, partner_financier_id, purchase_invoice_id, order_name, customer_id, payment_term_id
    ):
        """ Create purchase invoice line """
        # Get product_id
        product_template_id = self.env['product.template'].browse([partner_financier_id.product_id.id])
        product_id = self.env['product.product'].search([('product_tmpl_id', '=', product_template_id.id)])

        # Compute price unit
        price_unit = self.calculation_price_unit_line(payment_term_id)

        if product_id:
            product_name = f"{order_name} - {customer_id.name} - {payment_term_id.name}"
            new_line = self.env['account.move.line'].create({
                'move_id': purchase_invoice_id.id,
                'product_id': product_id.id,
                'name': product_name,
                'quantity': 1,
                'price_unit': price_unit,
            })

    def action_confirm(self):
        """ Surcharge base method """
        res = super(SaleOrder, self).action_confirm()
        if self.show_credit and self.payment_term_id.partner_financier_id:
            partner_financier_id = self.payment_term_id.partner_financier_id

            # Check control
            if len(partner_financier_id) > 1:
                raise UserError(
                    _("Problem with partner financier configuration. Many records exists for one financier"))
            if not partner_financier_id.product_id:
                raise UserError(_("Please configure the product corresponding to the management fees to continue"))

            purchase_invoice_id = self.create_purchase_invoice(partner_financier_id.partner_id)
            if purchase_invoice_id:
                self.message_post(body=_("Purchase invoice %s created", purchase_invoice_id.name))
                self.create_purchase_invoice_line(
                    partner_financier_id, purchase_invoice_id, self.name, self.partner_id, self.payment_term_id
                )
                self.message_post(body=_("Line created on purchase invoice"))

        return res
