# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    customer_id = fields.Many2one('res.partner', string="Final customer (Trading)", compute="_compute_customer_id")

    @api.depends('invoice_origin')
    def _compute_customer_id(self):
        """ Compute final customer for show into invoice """
        for move in self:
            customer_id = False
            order_id = self.env['sale.order'].search([('name', '=', move.invoice_origin)])
            if order_id and order_id.customer_id:
                customer_id = order_id.customer_id.id

            move.customer_id = customer_id
