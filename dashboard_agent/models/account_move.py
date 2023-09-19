# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _default_dashboard_agent(self):
        """ Get value dashboard agent by default """
        return self.env.context.get('dashboard_agent', False)

    dashboard_agent = fields.Boolean(string="Dashboard agent", default=_default_dashboard_agent)

    def _update_status_commission_associated(self, commission_order_id, new_state, body_msg):
        """ Update status commission associated """
        commission_order_id.write({
            'state': new_state,
        })
        self.message_post(body=body_msg)

    def _get_commission_order_associated(self):
        """ Get commission order associated """
        order_id = self.env['sale.order'].sudo().search([('name', '=', self.invoice_origin)])
        if order_id and order_id.dashboard_child_id:
            return order_id.dashboard_child_id

        return False

    def action_confirm_invoice_payment_for_agent(self):
        """ Validates the invoice payment to change the status of the agent commission """
        commission_order_id = self._get_commission_order_associated()
        if commission_order_id and commission_order_id.dashboard_commission_order:
            body_msg = f"L'état de la commission {commission_order_id.name} vient d'être modifié " \
                       f"pour 'Paiement client reçu'"
            self._update_status_commission_associated(commission_order_id, "customer_payment_received", body_msg)

    def action_confirm_commission_payment_for_agent(self):
        """ Validates the commission payment to change the status of the agent commission """
        commission_order_id = self._get_commission_order_associated()
        if commission_order_id and commission_order_id.dashboard_commission_order:
            body_msg = f"L'état de la commission {commission_order_id.name} vient d'être modifié pour 'Payé'"
            self._update_status_commission_associated(commission_order_id, "agorane_payed", body_msg)

    def action_post(self):
        """ Surcharge default function """
        res = super(AccountMove, self).action_post()
        commission_order_id = self._get_commission_order_associated()
        if commission_order_id and commission_order_id.dashboard_commission_order:
            body_msg = f"L'état de la commission {commission_order_id.name} vient d'être modifié pour 'Validé'"
            self._update_status_commission_associated(commission_order_id, "validated", body_msg)

        return res

    def action_dashboard_post(self):
        """ Force post invoice for principal agent """
        self.sudo().action_post()
