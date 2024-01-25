# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    dashboard_agent = fields.Boolean(string="Dashboard agent", compute="_compute_dashboard_agent")

    restrict_custom_field = fields.Boolean(
        string="Restrict custom field", compute="_compute_restrict_custom_field"
    )
    restrict_custom_field_d2r = fields.Boolean(
        string="Restrict custom field D2R", compute="_compute_restrict_custom_field_d2r"
    )
    restrict_custom_field_ka = fields.Boolean(
        string="Restrict custom field KA", compute="_compute_restrict_custom_field_ka"
    )

    @api.depends('invoice_user_id')
    def _compute_dashboard_agent(self):
        """ Allows you to display the page based on the seller """
        for move in self:
            dashboard_agent = False
            user_id = move.invoice_user_id
            if user_id.has_group('dashboard_agent.group_external_agent') or user_id.has_group(
                    'dashboard_agent.group_principal_agent'):
                dashboard_agent = True

            move.dashboard_agent = dashboard_agent

    @api.depends('name')
    def _compute_restrict_custom_field(self):
        """ Compute readonly custom field """
        for record in self:
            restrict_custom_field = False
            user = self.env.user
            if user.has_group('dashboard_agent.group_external_agent') or user.has_group('dashboard_agent.group_principal_agent'):
                restrict_custom_field = True

            record.restrict_custom_field = restrict_custom_field

    @api.depends('name')
    def _compute_restrict_custom_field_d2r(self):
        """ Compute readonly custom field D2R """
        for record in self:
            restrict_custom_field_d2r = False
            user = self.env.user
            if user.has_group('dashboard_agent.group_external_agent'):
                restrict_custom_field_d2r = True

            record.restrict_custom_field_d2r = restrict_custom_field_d2r

    @api.depends('name')
    def _compute_restrict_custom_field_ka(self):
        """ Compute readonly custom field KA """
        for record in self:
            restrict_custom_field_ka = False
            user = self.env.user
            if user.has_group('dashboard_agent.group_principal_agent'):
                restrict_custom_field_ka = True

            record.restrict_custom_field_ka = restrict_custom_field_ka

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
