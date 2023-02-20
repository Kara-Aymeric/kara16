# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    supplier_mail_template_id = fields.Many2one(comodel_name='mail.template', string="Mail template")
    supplier_quote_signed_mail_template_id = fields.Many2one(comodel_name='mail.template', string="Mail template")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        param = self.env['ir.config_parameter'].sudo()

        supplier_mail_template_id = param.get_param('custom_sale.supplier_mail_template_id')
        supplier_quote_signed_mail_template_id = param.get_param('custom_sale.supplier_quote_signed_mail_template_id')
        res.update(
            supplier_mail_template_id=int(supplier_mail_template_id),
            supplier_quote_signed_mail_template_id=int(supplier_quote_signed_mail_template_id),
        )

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        supplier_mail_template_id = self.supplier_mail_template_id.id \
            if len(self.supplier_mail_template_id) > 0 else False
        supplier_quote_signed_mail_template_id = self.supplier_quote_signed_mail_template_id.id \
            if len(self.supplier_quote_signed_mail_template_id) > 0 else False
        param.set_param('custom_sale.supplier_mail_template_id', supplier_mail_template_id)
        param.set_param('custom_sale.supplier_quote_signed_mail_template_id', supplier_quote_signed_mail_template_id)
