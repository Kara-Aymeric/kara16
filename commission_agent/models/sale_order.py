# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrderTags(models.Model):
    _inherit = "sale.order"

    state_payment_tag_id = fields.Selection(
        [('amount_received', 'Amount received'), ('amount_partially_received', 'Amount partially received')],
        string="State payment", help="State invoice payment", compute="_compute_state_payment_tag_id",
        store=True
    )
    #
    # @api.depends("invoice_ids", "invoice_ids.state", "invoice_ids.payment_state")
    # def _compute_state_payment_tag_id(self):
    #     for order in self:
    #
    #         res_tags = []
    #         amount_total_invoiced = sum(
    #             [
    #                 invoice.amount_total
    #                 for invoice in order.order_line.invoice_lines.move_id.filtered(
    #                     lambda r: r.move_type == "out_invoice" and r.state == "posted"
    #                 )
    #             ]
    #         )
    #
    #         amount_total_refunded = sum(
    #             [
    #                 invoice.amount_total
    #                 for invoice in rec.order_line.invoice_lines.move_id.filtered(
    #                     lambda r: r.move_type == "out_refund" and r.state == "posted"
    #                 )
    #             ]
    #         )
    #
    #         # Add invoice tag
    #         if amount_total_invoiced and invoice_tag:
    #             res_tags.append(invoice_tag.id)
    #
    #         # Refund tags
    #         if amount_total_invoiced and amount_total_refunded:
    #             # Add full refund tag if amount_total_invoice and amount_total_refunded have the same value.
    #             if amount_total_refunded == amount_total_invoiced and full_refund_tag:
    #                 res_tags.append(full_refund_tag.id)
    #             else:
    #                 # Partial refund tag
    #                 if amount_total_refunded and partial_refund_tag:
    #                     res_tags.append(partial_refund_tag.id)
    #         rec.invoice_tag_ids = [(6, 0, res_tags)]
