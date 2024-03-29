# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def _get_agent_partner_id_domain(self):
        """ Allows you to search only for contacts to agent """
        domain = []
        partner_ids = self.env['res.partner'].search([('user_id', '=', self.env.user.id)])
        if partner_ids:
            domain = [('id', 'in', partner_ids.ids)]

        return domain

    @api.model
    def _get_partner_id_domain(self):
        """ Surcharge method for add custom domain """
        res = super(CrmLead, self)._get_partner_id_domain()
        context = self.env.context

        dashboard_agent = False
        if context.get('dashboard_agent', False):
            dashboard_agent = True
        elif context.get('install_module', False) and context.get('install_module', False) == "dashboard_agent":
            dashboard_agent = True

        if dashboard_agent:
            res = []
            partner_ids = self.env['res.partner'].search([('user_id', '=', self.env.user.id)])
            if partner_ids:
                res = [('id', 'in', partner_ids.ids)]

        return res

    dashboard_agent = fields.Boolean(string="Dashboard agent", compute="_compute_dashboard_agent")
    partner_id = fields.Many2one(domain=_get_partner_id_domain)
    agent_partner_id = fields.Many2one(
        'res.partner', string="Customer", domain=_get_agent_partner_id_domain,
        help="Linked partner (optional). Usually created when converting the lead. "
             "You can find a partner by its Name, TIN, Email or Internal Reference."
    )

    @api.depends('user_id')
    def _compute_dashboard_agent(self):
        """ Allows you to display the page based on the seller """
        for lead in self:
            dashboard_agent = False
            user_id = lead.user_id
            if user_id.has_group('dashboard_agent.group_external_agent') or user_id.has_group(
                    'dashboard_agent.group_principal_agent'):
                dashboard_agent = True

            lead.dashboard_agent = dashboard_agent

    @api.onchange('agent_partner_id')
    def _onchange_agent_partner_id(self):
        """ Agent partner equal partner """
        self.partner_id = self.agent_partner_id.id
