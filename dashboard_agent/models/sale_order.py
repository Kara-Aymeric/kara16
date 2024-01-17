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
        'res.users', string="Principal agent", store=True, tracking=True
    )
    godfather_id = fields.Many2one(
        'res.users', string="Godfather", compute="_compute_godfather_id", store=True, readonly=False, tracking=True
    )
    is_validate_by_agent = fields.Boolean(
        string="Is validate", store=True, help="Is validate by principal agent", tracking=True
    )
    dashboard_agent = fields.Boolean(string="Dashboard agent", default=_default_dashboard_agent)

    dashboard_commission_order = fields.Boolean(string="Commission")
    dashboard_child_id = fields.Many2one(
        'sale.order',
        string="Associated commission",
        help="This sale allows to make the connection of the main sale for sale (commission)",
        copy=False
    )
    dashboard_order_origin_id = fields.Many2one('sale.order', string="Order origin", copy=False)
    dashboard_commission_total = fields.Monetary(
        string="Of which commission",
        store=True,
        compute="_compute_dashboard_commission_total",
        help="Total commission value for the sale", tracking=True)
    dashboard_associated_commission = fields.Boolean(string="Associated commission")
    dashboard_button_visible = fields.Boolean(
        string="Dashboard button visible",
        compute="_compute_dashboard_button_visible"
    )

    restrict_custom_field = fields.Boolean(
        string="Restrict custom field", compute="_compute_restrict_custom_field"
    )
    restrict_custom_field_d2r = fields.Boolean(
        string="Restrict custom field D2R", compute="_compute_restrict_custom_field_d2r"
    )
    restrict_custom_field_ka = fields.Boolean(
        string="Restrict custom field KA", compute="_compute_restrict_custom_field_ka"
    )

    @api.depends('user_id')
    def _compute_godfather_id(self):
        """ Get godfather """
        for order in self:
            godfather_id = order.godfather_id
            relation_agent_id = self.env['relation.agent'].sudo().search([
                ('godson_id', '=', order.user_id.id),
                ("start_date", "<=", fields.Date.today()),
                ("end_date", ">=", fields.Date.today())
            ], limit=1)
            if relation_agent_id:
                godfather_id = relation_agent_id.godfather_id

            order.godfather_id = godfather_id.id

    @api.depends('name')
    def _compute_restrict_custom_field(self):
        """ Compute readonly custom field """
        for record in self:
            restrict_custom_field = False
            user = self.env.user
            if user.has_group('dashboard_agent.group_external_agent') or user.has_group('dashboard_agent.group_principal_agent'):
                restrict_custom_field = True

            record.restrict_custom_field = restrict_custom_field

    @api.depends('name')
    def _compute_restrict_custom_field_d2r(self):
        """ Compute readonly custom field D2R """
        for record in self:
            restrict_custom_field_d2r = False
            user = self.env.user
            if user.has_group('dashboard_agent.group_external_agent'):
                restrict_custom_field_d2r = True

            record.restrict_custom_field_d2r = restrict_custom_field_d2r

    @api.depends('name')
    def _compute_restrict_custom_field_ka(self):
        """ Compute readonly custom field KA """
        for record in self:
            restrict_custom_field_ka = False
            user = self.env.user
            if user.has_group('dashboard_agent.group_principal_agent'):
                restrict_custom_field_ka = True

            record.restrict_custom_field_ka = restrict_custom_field_ka

    @api.depends('dashboard_agent', 'is_validate_by_agent')
    def _compute_dashboard_button_visible(self):
        """ Allows easy management of the display of buttons and fields in the dashboard module """
        for order in self:
            dashboard_button_visible = False
            if order.dashboard_agent and order.is_validate_by_agent:
                dashboard_button_visible = True

            order.dashboard_button_visible = dashboard_button_visible

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

    def _dashboard_check_agent_country(self):
        """ The country on the contact form is mandatory to continue. The tax depends on the country """
        if not self.user_id.partner_id.country_id:
            raise ValidationError(
                _("No country is configured for the agent (salespeople). This configuration is mandatory to set "
                  "an automatic tax when generating the quote of the 'commission' type")
            )

    def _dashboard_generate_commission_tax(self):
        """
        Search the tax for the agent. If the agent resides in France, the tax is 20%.
        If the agent resides outside France, then no tax is applied
        """
        self._dashboard_check_agent_country()
        commission_tax_id = self.env['account.tax'].search([('commission_tax', '=', True)])
        if not commission_tax_id:
            raise ValidationError(
                _("The configuration of a tax concerning the automatic creation of an estimate "
                  "of the type 'commission' is required to confirm the sale.\n"
                  "The company concerned by this configuration is %s", self.company_id.name)
            )
        if len(commission_tax_id) > 1:
            raise ValidationError(
                _("The tax for the automatic creation of the 'commission' type quote is unable to retrieve because "
                  "there are at least two taxes configured")
            )
        if self.user_id.partner_id.country_id.phone_code != 33:
            return False

        return [(4, commission_tax_id.id)]

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
                tax = order._dashboard_generate_commission_tax()
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
                customer_id = self.env.company.partner_id
                if order.dashboard_child_id:
                    # Replace all line
                    order.dashboard_child_id.write({
                        'order_line': False,
                    })
                    order.dashboard_child_id.write({
                        'order_line': [(0, 0, data) for data in prepare_values],
                    })
                else:
                    # Create new order with commission line
                    child_id = order.copy({
                        'name': order.name.replace("S", "C"),
                        'dashboard_commission_order': True,
                        'dashboard_order_origin_id': order.id,
                        'partner_id': customer_id.id,
                        'partner_invoice_id': customer_id.id,
                        'partner_shipping_id': customer_id.id,
                        'agent_partner_id': customer_id.id,
                        'agent_partner_invoice_id': customer_id.id,
                        'agent_partner_shipping_id': customer_id.id,
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

    def action_validate_quote(self):
        """ Validate quote by principal agent """
        self.ensure_one()
        self.write({'is_validate_by_agent': True})

    def action_cancel_request(self):
        """ Cancel quote by principal agent """
        self.ensure_one()
        self.write({'is_validate_by_agent': False})

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
