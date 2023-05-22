# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    agent_commission = fields.Float(string="Commission")
    agent_discount_commission = fields.Float(string="Discount commission")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter'].sudo()

        agent_commission = param.get_param('woo_user_connector.agent_commission')
        agent_discount_commission = param.get_param('woo_user_connector.agent_discount_commission')
        res.update(
            agent_commission=float(agent_commission),
            agent_discount_commission=float(agent_discount_commission),
        )

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        agent_commission = self.agent_commission or False
        agent_discount_commission = self.agent_discount_commission or False

        param.set_param('woo_user_connector.agent_commission', agent_commission)
        param.set_param('woo_user_connector.agent_discount_commission', agent_discount_commission)
