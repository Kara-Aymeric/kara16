# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


READONLY_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'sale', 'done', 'cancel'}
}

LOCKED_FIELD_STATES = {
    state: [('readonly', True)]
    for state in {'done', 'cancel'}
}


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

    @api.model
    def _get_agent_partner_invoice_id_domain(self):
        """ Allows you to search only for contacts to agent (partner invoice address) """
        domain = []
        partner_ids = self.env['res.partner'].search([('user_id', '=', self.env.user.id)])
        if partner_ids:
            domain = ['|',
                      ('company_id', '=', False),
                      ('company_id', '=', self.company_id),
                      ('id', 'in', partner_ids.ids)]

        return domain

    @api.model
    def _get_agent_partner_shipping_id_domain(self):
        """ Allows you to search only for contacts to agent (partner invoice address) """
        domain = []
        partner_ids = self.env['res.partner'].search([('user_id', '=', self.env.user.id)])
        if partner_ids:
            domain = ['|',
                      ('company_id', '=', False),
                      ('company_id', '=', self.company_id),
                      ('id', 'in', partner_ids.ids)]

        return domain

    def _default_dashboard_agent(self):
        """ Get value dashboard agent by default """
        return self.env.context.get('dashboard_agent', False)

    state = fields.Selection(
        selection_add=[
            ('validated', "Validated"),
            ('customer_payment_received', "Customer payment received"),
            ('agorane_payed', "Payed")
        ]
    )

    agent_partner_id = fields.Many2one(
        'res.partner', string="Customer", domain=_get_agent_partner_id_domain,
        readonly=False, change_default=True, index=True, tracking=1,
        states=READONLY_FIELD_STATES
    )

    agent_partner_invoice_id = fields.Many2one(
        'res.partner', string="Invoice Address", domain=_get_agent_partner_invoice_id_domain,
        compute='_compute_agent_partner_invoice_id',
        store=True, readonly=False, precompute=True,
        states=LOCKED_FIELD_STATES
    )

    agent_partner_shipping_id = fields.Many2one(
        'res.partner', string="Delivery Address", domain=_get_agent_partner_shipping_id_domain,
        compute='_compute_agent_partner_shipping_id',
        store=True, readonly=False, precompute=True,
        states=LOCKED_FIELD_STATES
    )

    principal_agent_id = fields.Many2one(
        'res.users', string="Principal agent", compute="_compute_principal_agent_id", store=True, tracking=True
    )
    is_validate_by_agent = fields.Boolean(string="Is validate", help="Is validate by principal agent")
    dashboard_agent = fields.Boolean(string="Dashboard agent", default=_default_dashboard_agent)

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

    @api.depends('agent_partner_id')
    def _compute_agent_partner_invoice_id(self):
        for order in self:
            order.agent_partner_invoice_id = order.agent_partner_id.address_get(['invoice'])['invoice'] \
                if order.agent_partner_id else False

    @api.depends('agent_partner_id')
    def _compute_agent_partner_shipping_id(self):
        for order in self:
            order.agent_partner_shipping_id = order.agent_partner_id.address_get(['delivery'])['delivery'] \
                if order.agent_partner_id else False

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

    def _dashboard_create_order_child(self):
        """
        Creation of a child sale if commission lines exist and addition of commission lines on
        the new sale for the manufacturer
        """
        for order in self:
            prepare_values = []
            company_user = self.env.user.company_id

            if order.dashboard_commission_total > 0:
                # Prepare data for add commission line
                tax = order._generate_commission_tax()
                product_id = self.env['product.product'].search(
                    [('product_tmpl_id', '=', self.env.ref("dashboard_agent.dashboard_product_template_commission").id)]
                )
                commission_name = f"Commission pour {order.partner_id.name}. " \
                                  f"Commande N°{order.name or ''}"
                prepare_values = [{
                    'name': commission_name,
                    'product_id': product_id.id,
                    'product_uom_qty': 1,
                    'tax_id': tax if tax else False,
                    'price_unit': order.dashboard_commission_total,
                    'company_id': company_user.id,
                }]
            if len(prepare_values) > 0:
                if order.dashboard_child_id:
                    # Replace all line
                    order.dashboard_child_id.order_line = False
                    order.dashboard_child_id.write({
                        'order_line': [(0, 0, data) for data in prepare_values],
                    })
                else:
                    # Create new order with commission line
                    child_id = order.copy({
                        'dashboard_commission_order': True,
                        'dashboard_order_origin_id': order.id,
                        'order_line': [(0, 0, data) for data in prepare_values],
                    })

                    # Affiliate order child into order
                    order.write({
                        'dashboard_associated_commission': True,
                        'dashboard_child_id': child_id.id,
                    })

    def action_confirm(self):
        """ Surcharge base function """
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            if order.dashboard_agent:
                order._dashboard_create_order_child()
        return res

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

    @api.onchange('agent_partner_invoice_id')
    def _onchange_agent_partner_invoice_id(self):
        """ Agent partner invoice address equal partner invoice address """
        self.partner_invoice_id = self.agent_partner_invoice_id.id

    @api.onchange('agent_partner_shipping_id')
    def _onchange_agent_partner_shipping_id(self):
        """ Agent partner shipping address equal partner shipping address """
        self.partner_shipping_id = self.agent_partner_shipping_id.id
