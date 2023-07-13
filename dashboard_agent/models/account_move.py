# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_confirm_payment_for_agent(self):
        """ Validates the payment to change the status of the agent commission """
        print("OK")
