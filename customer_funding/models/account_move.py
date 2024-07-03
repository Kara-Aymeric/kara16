# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

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
            elif based_on == "total_amount_purchase":
                # Get origin order
                order_id = self.env['sale.order'].sudo().search([('name', '=', self.invoice_origin)])
                if order_id:
                    # Get purchase order
                    purchase_order_id = self.env['purchase.order'].sudo().search([('origin', '=', order_id.name)])
                    if purchase_order_id:
                        # Get invoice_ids
                        purchase_invoice_ids = purchase_order_id.invoice_ids
                        purchase_invoice_amount_total = 0
                        for invoice_id in purchase_invoice_ids:
                            purchase_invoice_amount_total += invoice_id.amount_total

                        return purchase_invoice_amount_total * (payment_term_id.management_fees/100)
                    return False
                return False
            return False
        return False

    def create_purchase_invoice_line(
            self, partner_financier_id, purchase_invoice_id, order_name, customer_id, payment_term_id
    ):
        """ Create purchase invoice line """
        # Get product_id
        product_template_id = self.env['product.template'].browse([partner_financier_id.product_id.id])
        product_id = self.env['product.product'].search([('product_tmpl_id', '=', product_template_id.id)])

        # Compute price unit
        price_unit_calculation = self.calculation_price_unit_line(payment_term_id)

        if product_id:
            product_name = f"{order_name} - {customer_id.name} - {payment_term_id.name}"
            price_unit = price_unit_calculation if price_unit_calculation else 0
            new_line = self.env['account.move.line'].create({
                'move_id': purchase_invoice_id.id,
                'product_id': product_id.id,
                'name': product_name,
                'quantity': 1,
                'price_unit': price_unit,
            })

    def action_post(self):
        """ Surcharge base method """
        res = super(AccountMove, self).action_post()
        if self.move_type == "out_invoice":
            if self.invoice_payment_term_id and self.invoice_payment_term_id.partner_financier_id:
                partner_financier_id = self.invoice_payment_term_id.partner_financier_id

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
                        partner_financier_id, purchase_invoice_id, self.invoice_origin,
                        self.partner_id, self.invoice_payment_term_id
                    )
                    self.message_post(body=_("Line created on purchase invoice"))

        return res
