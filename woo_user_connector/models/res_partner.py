# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    agent_commission = fields.Float(
        string="Commission",
        tracking=True,
    )

    agent_discount_commission = fields.Float(
        string="Discount commission",
        tracking=True
    )

    website_account = fields.Boolean(string="Website account")

    @api.onchange('agent_commission')
    def _onchange_agent_commission(self):
        """ Agent commission must be greater than 0. """
        user = self.env.user
        if self.agent_commission <= 0:
            if not user.has_group('dashboard_agent.group_admin'):
                raise ValidationError(_("Agent commission must be greater than 0."))

    @api.onchange('agent_discount_commission')
    def _onchange_agent_discount_commission(self):
        """ Agent discount commission must be greater than 0. """
        user = self.env.user
        if self.agent_discount_commission <= 0:
            if not user.has_group('dashboard_agent.group_admin'):
                raise ValidationError(_("Agent commission must be greater than 0."))

    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id:
            self.write({
                'agent_commission': self.user_id.agent_commission,
                'agent_discount_commission': self.user_id.agent_discount_commission,
            })
