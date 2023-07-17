# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _default_dashboard_agent(self):
        """ Get value dashboard agent by default """
        return self.env.context.get('dashboard_agent', False)

    dashboard_agent = fields.Boolean(string="Dashboard agent", default=_default_dashboard_agent)

    def action_confirm_payment_for_agent(self):
        """ Validates the payment to change the status of the agent commission """
        print("OK")
