# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_agent_partner_id_domain(self):
        """ Allows you to search only for contacts to agent """
        domain = []
        partner_ids = self.env['res.partner'].search([('user_id', '=', self.env.user.id)])
        if partner_ids:
            domain = [('id', 'in', partner_ids.ids)]

        return domain

    state = fields.Selection(
        selection_add=[
            ('validated', "Validated"),
            ('customer_payment_received', "Customer payment received"),
            ('agorane_payed', "Payed")
        ]
    )

    agent_partner_id = fields.Many2one(
        'res.partner', string="Customer", domain=_get_agent_partner_id_domain, tracking=True
    )
    principal_agent_id = fields.Many2one(
        'res.users', string="Principal agent", compute="_compute_principal_agent_id", store=True, tracking=True
    )
    is_validate_by_agent = fields.Boolean(string="Is validate", help="Is validate by principal agent")
    dashboard_agent = fields.Boolean(string="Dashboard agent", compute="_compute_dashboard_agent")

    dashboard_commission_order = fields.Boolean(string="Commission")
    dashboard_child_id = fields.Many2one(
        'sale.order',
        string="Associated commission",
        help="This sale allows to make the connection of the main sale for sale (commission)")
    dashboard_order_origin_id = fields.Many2one('sale.order', string="Order origin")
    dashboard_commission_total = fields.Monetary(
        string="Of which commission",
        store=True,
        compute="_compute_dashboard_commission_total",
        help="Total commission value for the sale", tracking=True)
    dashboard_associated_commission = fields.Boolean(string="Associated commission")

    @api.depends('order_line.dashboard_price_commission')
    def _compute_dashboard_commission_total(self):
        for order in self:
            amount_commission = 0.0
            for line in order.order_line:
                amount_commission += line.dashboard_price_commission
            order.dashboard_commission_total = amount_commission

    @api.depends('user_id')
    def _compute_principal_agent_id(self):
        """ Allows to link the main agent to the seller """
        for record in self:
            principal_agent_id = False
            for relation_agent in self.env['relation.agent'].search([]):
                if record.user_id in relation_agent.mapped('agent_ids'):
                    principal_agent_id = relation_agent.principal_agent_id.id

            record.principal_agent_id = principal_agent_id

    @api.depends_context('dashboard_agent')
    def _compute_dashboard_agent(self):
        for record in self:
            record.dashboard_agent = self.env.context.get('dashboard_agent', False)

    def action_quote_confirmation_request(self):
        """ Opens a wizard to compose an email, with relevant mail template loaded by default """
        self.ensure_one()

        # Get partner mail template
        template_id = self.env['ir.config_parameter'].sudo(). \
            get_param('dashboard_agent.quote_notification_template_id', default=False)
        template_id = int(template_id)

        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'force_email': True,
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    @api.onchange('agent_partner_id')
    def _onchange_agent_partner_id(self):
        """ Agent partner equal partner """
        self.partner_id = self.agent_partner_id.id

    @api.onchange('partner_id')
    def _onchange_agorane_partner_id(self):
        """ Partner equal agent partner """
        self.agent_partner_id = self.partner_id.id
