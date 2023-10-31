# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    quote_notification_template_id = fields.Many2one(
        comodel_name='mail.template',
        string="Email template"
    )
    sponsorship_duration = fields.Integer(
        string="Sponsorship duration",
        help="Sponsorship time. Allows you to automatically calculate "
             "the sponsorship end date when adding a new relationship"
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter'].sudo()

        quote_notification_template_id = param.get_param('dashboard_agent.quote_notification_template_id')
        sponsorship_duration = param.get_param('dashboard_agent.sponsorship_duration')
        res.update(
            quote_notification_template_id=int(quote_notification_template_id),
            sponsorship_duration=int(sponsorship_duration),
        )

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        quote_notification_template_id = self.quote_notification_template_id.id \
            if len(self.quote_notification_template_id) > 0 else False
        sponsorship_duration = self.sponsorship_duration or False

        param.set_param('dashboard_agent.quote_notification_template_id', quote_notification_template_id)
        param.set_param('dashboard_agent.sponsorship_duration', sponsorship_duration)
