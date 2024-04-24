# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    is_payment_reminder = fields.Boolean(
        string="Enable payment reminder",
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter'].sudo()

        is_payment_reminder = param.get_param('custom_payment_reminder.is_payment_reminder')
        res.update(is_payment_reminder=is_payment_reminder)

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        is_payment_reminder = self.is_payment_reminder
        param.set_param('custom_payment_reminder.is_payment_reminder', is_payment_reminder)
