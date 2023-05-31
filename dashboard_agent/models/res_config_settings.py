# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    quote_notification_template_id = fields.Many2one(
        comodel_name='mail.template',
        string="Email template"
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter'].sudo()

        quote_notification_template_id = param.get_param('dashboard_agent.quote_notification_template_id')
        res.update(
            quote_notification_template_id=int(quote_notification_template_id),
        )

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        quote_notification_template_id = self.quote_notification_template_id.id \
            if len(self.quote_notification_template_id) > 0 else False

        param.set_param('dashboard_agent.quote_notification_template_id', quote_notification_template_id)
