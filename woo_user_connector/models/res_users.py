# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = 'res.users'

    def _get_default_agent_commission(self):
        """ Get default agent commission configured in the general settings of the Sales module """
        agent_commission = self.env['ir.config_parameter'].sudo(). \
            get_param('woo_user_connector.agent_commission', default=False)

        return agent_commission

    def _get_default_agent_discount_commission(self):
        """ Get default agent discount commission configured in the general settings of the Sales module """
        agent_discount_commission = self.env['ir.config_parameter'].sudo(). \
            get_param('woo_user_connector.agent_discount_commission', default=False)

        return agent_discount_commission

    agent_reference = fields.Char(
        string="Agent reference",
        help="This (unique) reference makes it possible to link WooCommerce and Odoo when creating a contact "
             "account from WooCommerce. This code also allows the default allocation of a commission for this contact.",
        required=True
    )

    agent_commission = fields.Float(
        string="Commission",
        help="When creating a contact from WooCommerce, this commission is recovered for "
             "the assigned to the created contact.",
        default=_get_default_agent_commission
    )

    agent_discount_commission = fields.Float(
        string="Discount commission",
        help="When creating a contact from WooCommerce, this commission is recovered for "
             "the assigned to the created contact.",
        default=_get_default_agent_discount_commission
    )

    @api.constrains('agent_reference')
    def _check_agent_reference(self):
        """ Allows to have only one record with this agent reference """
        for user in self:
            if user.agent_reference and self.search_count([('agent_reference', '=', user.agent_reference)]) > 1:
                raise ValidationError(_("The agent reference is already assigned."))
