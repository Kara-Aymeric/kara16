# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def _default_dashboard_agent(self):
        """ Get value dashboard agent by default """
        return self.env.context.get('dashboard_agent', False)

    @api.model
    def _get_partner_id_domain(self):
        """ Surcharge method for add custom domain """
        res = super(CrmLead, self)._get_partner_id_domain()
        context = self.env.context
        if context.get('dashboard_agent', False):
            partner_ids = self.env['res.partner'].search([('user_id', '=', self.env.user.id)])
            if partner_ids:
                res = [('id', 'in', partner_ids.ids)]

        return res

    dashboard_agent = fields.Boolean(string="Dashboard agent", default=_default_dashboard_agent)
    partner_id = fields.Many2one(domain=_get_partner_id_domain)
