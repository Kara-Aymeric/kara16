# -*- coding: utf-8 -*-
import logging
import timeit
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError


_logger = logging.getLogger(__name__)


class CommissionAgent(models.Model):
    _name = "commission.agent"
    _rec_name = "commission_rule_id"
    _description = "Commission agent generated automatically"

    log_tracking = fields.Char(related="commission_rule_id.log_tracking", readonly=True)
    name = fields.Char(string="Name", compute="_compute_name", store=True, readonly=False)
    agent_id = fields.Many2one("res.users", string="Agent", required=True)
    date = fields.Date(string="Commission Date", required=True)
    commission_rule_id = fields.Many2one("commission.agent.rule", string="Commission Rule")
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id, readonly=True
    )
    amount = fields.Monetary(string="Commission amount", compute="_compute_amount", store=True)
    amount_force = fields.Monetary(string="Amount", compute="_compute_amount_force", readonly=False, store=True)
    is_invoiced = fields.Boolean(string="Is invoiced")
    purchase_invoice_id = fields.Many2one("account.move", string="Invoice supplier")
    is_sponsorship_rule = fields.Boolean(string="Is sponsorship rule", related="commission_rule_id.is_sponsorship_rule")
    commission_agent_calcul_ids = fields.One2many(
        "commission.agent.calcul", "commission_agent_id", string="Commission agent calcul", required=True
    )
    special_commission = fields.Char(string="Commission name", help="Display name into invoice line")
    edit_mode = fields.Boolean(string="Edit mode", default=True)
    restrict_fields = fields.Boolean(string="Restrict fields")

    @api.depends('log_tracking')
    def _compute_name(self):
        """ Compute name depending log_tracking. If edit mode, edit name manually """
        for commission in self:
            name = ""
            if commission.log_tracking:
                name = commission.log_tracking

            commission.name = name

    @api.depends('amount')
    def _compute_amount_force(self):
        """ Compute amount force depending amount. If edit mode, edit amount manually """
        for commission in self:
            amount_force = commission.amount_force
            if commission.amount:
                amount_force = commission.amount

            commission.amount_force = amount_force

    @api.depends('commission_rule_id', 'commission_agent_calcul_ids', 'commission_agent_calcul_ids.result')
    def _compute_amount(self):
        """ Compute amount depending result from calcul details """
        for commission in self:
            amount = 0
            if commission.commission_rule_id and commission.commission_agent_calcul_ids:
                amount_list = commission.commission_agent_calcul_ids.mapped('result')
                amount = sum(sub for sub in amount_list)
            commission.amount = amount

    def _get_active_rules(self):
        """ Get all active rules for calculation commission by agent """
        rules = self.env["commission.agent.rule"].search([
            "|",
            ("start_date", "=", False),
            ("start_date", "<=", fields.Date.today()),
            "|",
            ("expiration_date", "=", False),
            ("expiration_date", ">=", fields.Date.today())
        ])

        return rules

    def _update_synchronization_history(self, type_sync, comment, sync_ok):
        self.env['synchronization.commission.history'].create({
            'type': "automatic" if type_sync == "automatic" else "manual",
            'name': self.env.user.name,
            'message': comment,
            'sync_ok': sync_ok,
        })

    def _get_active_commission_specific_agent(self, rule):
        """ Get active agent to rule """
        commission_specific_agent_ids = self.env['commission.specific.agent'].search([
            ('rule_id', '=', rule.id),
            "|",
            ("start_date", "=", False),
            ("start_date", "<=", fields.Date.today()),
            "|",
            ("end_date", "=", False),
            ("end_date", ">=", fields.Date.today())
        ])
        return commission_specific_agent_ids

    def _get_all_partner_orders(self, type_rule, partner, agent):
        """ Get all orders for search invoices associated """
        orders = []
        domain_order = [
            ('id', 'in', partner.sale_order_ids.mapped('id')),
            ('amount_untaxed', '>', 0),
        ]
        order_ids = self.env['sale.order'].search(domain_order, order="id asc")
        for order in order_ids:
            if type_rule == "new_customer":
                if order.user_id.id != agent.id:
                    return []
            if order.user_id.id == agent.id and order.invoice_ids:
                orders.append(order.id)

        return orders

    def _get_invoice_payed(self, agent, invoice_ids):
        """ Get invoice payed for calculation commission by agent """
        domain_invoice = [
            ('id', 'in', invoice_ids),
            ('state', '=', "posted"),
            ('invoice_user_id', '=', agent.id),
            ('move_type', '=', "out_invoice"),
            ('payment_state', 'in', ["in_payment", "paid", "reversed"]),
        ]
        invoices = self.env['account.move'].search(domain_invoice, order="invoice_date asc")
        if invoices:
            return invoices.mapped('id')
        return []

    def _get_refund_payed(self):
        """ Get out refund payed for calculation commission by agent """
        domain = [
            ('state', '=', "posted"),
            ('move_type', '=', "out_refund"),
            ('payment_state', 'in', ["in_payment", "paid"]),
        ]
        invoices = self.env['account.move'].search(domain, order="invoice_date asc")

        return invoices.mapped('id')

    def _get_result_commission(self, rule, invoice):
        """ Return amount fixe or percentage result to amount untaxed to invoice """
        if rule.result_type == "amount":
            return rule.result_amount
        elif rule.result_type == "percent":
            return rule.result_percent * invoice.amount_untaxed

    def _create_commission_calcul(self, rule, agent, invoice, delta=False):
        """ Create a commission calcul """
        if not delta:
            order_id = self.env['sale.order'].search([('name', '=', invoice.invoice_origin)])
            vals = {
                "agent_id": agent.id,
                "order_id": order_id.id if order_id else False,
                "rule_id": rule.id,
                "result": self._get_result_commission(rule, invoice),
                "commission_date": invoice.commission_date,
            }

            # Create commission calcul
            return self.env['commission.agent.calcul'].create(vals)
        else:
            invoice_date = invoice.mapped('invoice_date')

    def _get_couting(self, rule):
        """ Get commission rule condition """
        for condition in rule.condition_rule_ids:
            if condition.value:
                return condition.value

    def _get_delta(self, rule):
        """ Get delta if cumulative rule condition """
        if rule.is_cumulative:
            for cumulative_with_id in rule.cumulative_with_ids:
                if cumulative_with_id.delta:
                    return cumulative_with_id.delta

    def _get_target_invoices(self, type_rule, partner, agent, start_date, counting_order_new_customer):
        """ Get target invoices for calculation commission """
        all_invoice_list = []
        all_orders = self.env['sale.order'].browse(self._get_all_partner_orders(type_rule, partner, agent))
        for order in all_orders:
            if order.date_order.date() >= start_date:
                all_invoice_list += (
                    self._get_invoice_payed(agent, order.invoice_ids.mapped('id'))
                )
        invoices = self.env['account.move'].search([
            ('id', 'in', all_invoice_list)
        ], order="invoice_date asc", limit=counting_order_new_customer
        )
        return invoices

    def _generate_commission_new_customer(self, rule, agent, start_date):
        """ Generate commission type equals new customer order """
        counting_order_new_customer = self._get_couting(rule)
        if rule.is_cumulative:
            calcul_list = []
            rule_cumulative_id = rule.cumulative_with_ids
            delta = self._get_delta(rule)
            for commission_calcul in self.env['commission.agent.calcul'].search([
                ('rule_id', '=', rule_cumulative_id.rule_id.id)
            ]):
                invoices = self._get_target_invoices(
                    "new_customer", commission_calcul.partner_id, agent, start_date, counting_order_new_customer
                )
                if invoices and len(invoices) == counting_order_new_customer:
                    last_invoice = self.env['account.move'].browse(invoices.mapped('id')[-1])
                    invoice_date_list = invoices.mapped('invoice_date')
                    invoice_date_delta = invoice_date_list[-1] - invoice_date_list[-2]
                    if invoice_date_delta.days <= delta:
                        calcul_ids = self._create_commission_calcul(rule, agent, last_invoice)
                        calcul_list += calcul_ids.mapped('id')
            return calcul_list

        else:
            calcul_list = []
            for partner in self.env['res.partner'].search([('user_id', '=', agent.id)]):
                if partner.sale_order_ids:
                    invoices = self._get_target_invoices("new_customer", partner, agent, start_date, counting_order_new_customer)
                    if invoices:
                        calcul_ids = self._create_commission_calcul(rule, agent, invoices)
                        calcul_list += calcul_ids.mapped('id')
            return calcul_list

    def _create_commission_agent(self, calcul_list):
        """ Create commission agent depending commission calcul """
        commission_agent_calcul_ids = self.env['commission.agent.calcul'].search(
            [('id', 'in', calcul_list)], order="rule_id asc"
        )
        for calcul in commission_agent_calcul_ids:
            commission_agent_id = self.env['commission.agent'].search([
                ('commission_rule_id', '=', calcul.rule_id.id),
                ('agent_id', '=', calcul.agent_id.id),
                ('date', '=', calcul.commission_date),
            ])
            if commission_agent_id:
                # Create commission agent (global by rules)
                commission_agent_id.write({
                    'commission_agent_calcul_ids': [(4, calcul.id)],
                })
            else:
                # Create commission agent (global by rules)
                self.env['commission.agent'].create({
                    'date': calcul.commission_date,
                    'agent_id': calcul.agent_id.id,
                    'edit_mode': False,
                    'restrict_fields': True,
                    'commission_rule_id': calcul.rule_id.id,
                    'commission_agent_calcul_ids': [(4, calcul.id)],
                })

    def _generate_commission_specific_customer(self, rule, agent, start_date, customer_ids):
        """ Generate commission type equals specific customer """
        calcul_list = []
        for partner in self.env['res.partner'].search([
            ('user_id', '=', agent.id),
            ('id', 'in', customer_ids.ids)
        ]):
            if partner.sale_order_ids:
                invoices = self._get_target_invoices("commission_specific", partner, agent, start_date, 10000)
                for invoice in invoices:
                    calcul_ids = self._create_commission_calcul(rule, agent, invoice)
                    calcul_list += calcul_ids.mapped('id')

        return calcul_list

    def _generate_base_commission(self):
        """ Generate base commission for show into calcul """
        calcul_list = []
        commission_base_rule = self.env.ref("commission_agent.commission_base_rule", False)
        if commission_base_rule:
            for commission in self.env['sale.order'].search([('dashboard_order_origin_id', '!=', False)]):
                if self._get_invoice_payed(
                        commission.user_id, commission.dashboard_order_origin_id.invoice_ids.mapped('id')
                ):
                    vals = {
                        "agent_id": commission.user_id.id,
                        "order_id": commission.id,
                        "rule_id": commission_base_rule.id,
                        "result": commission.amount_untaxed,
                        "commission_date": commission.commission_date,
                    }
                    # Create commission calcul
                    commission_agent_calcul_id = self.env['commission.agent.calcul'].create(vals)
                    calcul_list += commission_agent_calcul_id.mapped('id')

        return calcul_list

    def _generate_sponsorship_commission(self):
        """ Generate sponsorship commission for show into calcul """
        calcul_list = []
        commission_sponsorship_rule = self.env.ref("commission_agent.commission_sponsorship_rule", False)
        if commission_sponsorship_rule:
            not_calculation_sponsorship_rule_ids = self.env['commission.agent.rule'].search(
                [('is_not_calculation_sponsorship', '=', True)]
            )

            for sponsorship in self.env['relation.agent'].search([]):
                godson_id = sponsorship.godson_id
                godfather_id = sponsorship.godfather_id
                percentage_commission = sponsorship.commission
                calcul_order_list = []
                agent_order_list = []
                godson_order_ids = self.env['sale.order'].search([
                    ('user_id', '=', godson_id.id),
                    ('date_order', '>=', sponsorship.start_date),
                    ('date_order', '<=', sponsorship.end_date),
                ])

                domain_calcul = [('agent_id', '=', godson_id.id)]
                if not_calculation_sponsorship_rule_ids:
                    domain_calcul += [('rule_id', 'not in', not_calculation_sponsorship_rule_ids.mapped('id'))]
                commission_agent_calcul_ids = self.env['commission.agent.calcul'].search(domain_calcul)

                if commission_agent_calcul_ids:
                    order_ids = commission_agent_calcul_ids.mapped('order_id')
                    calcul_order_list = order_ids.ids
                if godson_order_ids:
                    agent_order_list = godson_order_ids.ids

                if godson_order_ids:
                    # target_sales = [x for x in agent_order_list if x not in calcul_order_list]  # A CORRIGER !
                    target_sales = list(set(calcul_order_list) & set(agent_order_list))
                    for order in self.env['sale.order'].browse(target_sales):
                        if self._get_invoice_payed(godson_id, order.invoice_ids.mapped('id')):
                            vals = {
                                "agent_id": godfather_id.id,
                                "godson_id": order.user_id.id,
                                "order_id": order.id,
                                "rule_id": commission_sponsorship_rule.id,
                                "result": percentage_commission * order.amount_untaxed,
                                "commission_date": order.commission_date,
                            }
                            # Create commission calcul
                            commission_agent_calcul_id = self.env['commission.agent.calcul'].create(vals)
                            calcul_list += commission_agent_calcul_id.mapped('id')

        return calcul_list

    def _generate_new_result(self, invoice_refund, commission_recovery_rule, commission_calcul_ids):
        """ """
        calcul_list = []
        for commission_calcul in commission_calcul_ids:
            if commission_calcul.rule_id:
                delta_amount = False
                new_result = False
                # Stocker facture en amont
                invoice_origin_id = self.env['account.move'].search(
                    [('reversal_move_id', 'in', invoice_refund.mapped("id"))]
                )
                if invoice_origin_id:
                    origin_amount_untaxed_signed = invoice_origin_id.amount_untaxed_signed
                    delta_amount = invoice_refund.amount_untaxed_signed + origin_amount_untaxed_signed
                    inverse_refund_amount = - invoice_refund.amount_untaxed_signed

                    # Proportional calcul
                    new_result = (
                        - ((invoice_refund.amount_untaxed_signed * commission_calcul.result) /
                           origin_amount_untaxed_signed)
                    )

                # Si delta = 0 alors avoir total donc reprise de toutes les primes
                if delta_amount == 0:
                    if commission_calcul.rule_id.total_recovery_on_refund:
                        vals = {
                            "agent_id": commission_calcul.agent_id.id,
                            "godson_id": commission_calcul.godson_id.id,
                            "order_id": commission_calcul.order_id.id,
                            "rule_id": commission_recovery_rule.id,
                            "result": - commission_calcul.result,
                            "commission_date": invoice_refund.invoice_date,
                        }
                        commission_agent_calcul_id = self.env['commission.agent.calcul'].create(vals)
                        calcul_list += commission_agent_calcul_id.mapped('id')
                    else:
                        vals = {
                            "agent_id": commission_calcul.agent_id.id,
                            "godson_id": commission_calcul.godson_id.id,
                            "order_id": commission_calcul.order_id.id,
                            "rule_id": commission_recovery_rule.id,
                            "result": - new_result or 0,
                            "commission_date": invoice_refund.invoice_date,
                        }
                        commission_agent_calcul_id = self.env['commission.agent.calcul'].create(vals)
                        calcul_list += commission_agent_calcul_id.mapped('id')
                else:
                    if not commission_calcul.rule_id.total_recovery_on_refund:
                        vals = {
                            "agent_id": commission_calcul.agent_id.id,
                            "godson_id": commission_calcul.godson_id.id,
                            "order_id": commission_calcul.order_id.id,
                            "rule_id": commission_recovery_rule.id,
                            "result": - new_result or 0,
                            "commission_date": invoice_refund.invoice_date,
                        }
                        commission_agent_calcul_id = self.env['commission.agent.calcul'].create(vals)
                        calcul_list += commission_agent_calcul_id.mapped('id')

        return calcul_list

    def calculate_commission_refund(self):
        """ Calculate commission refund """
        calcul_list = []
        all_refund_list = self._get_refund_payed()
        commission_recovery_rule = self.env.ref("commission_agent.commission_recovery_rule", False)
        if not commission_recovery_rule:
            raise ValidationError(
                _("Recovery rule not found !")
            )
        invoice_refund_ids = self.env['account.move'].search([('id', 'in', all_refund_list)], order="invoice_date asc")
        for invoice_refund in invoice_refund_ids:
            commission_order_id = False
            order_id = self.env['sale.order'].search([('invoice_ids', 'in', invoice_refund.mapped('id'))], limit=1)
            if order_id:
                commission_order_id = order_id.dashboard_child_id
            if order_id:
                commission_calcul_ids = self.env['commission.agent.calcul'].search([('order_id', '=', order_id.id)])
                calcul_list += self._generate_new_result(invoice_refund, commission_recovery_rule, commission_calcul_ids)
            if commission_order_id:
                commission_order_calcul_ids = self.env['commission.agent.calcul'].search([('order_id', '=', commission_order_id.id)])
                calcul_list += self._generate_new_result(invoice_refund, commission_recovery_rule, commission_order_calcul_ids)

        return calcul_list

    def calculate_commission(self, type_sync="automatic", comment=""):
        """ Action synchronize """
        # Clear records
        self.env['commission.agent.calcul'].search([]).unlink()
        self.env['commission.agent'].search([]).unlink()

        rules = self._get_active_rules()
        calcul_list = []
        for rule in rules:
            _logger.info(rule.name)
            commission_specific_agent_ids = self._get_active_commission_specific_agent(rule)
            apply_on = rule.applies_on
            for commission_specific_agent in commission_specific_agent_ids:
                agent = commission_specific_agent.agent_id
                agent_start_date = commission_specific_agent.start_date or False
                if apply_on == "new_customer_order":
                    calcul_list += self._generate_commission_new_customer(rule, agent, agent_start_date)
                elif apply_on == "specific_customer":
                    customer_ids = commission_specific_agent.customer_ids
                    calcul_list += self._generate_commission_specific_customer(
                        rule, agent, agent_start_date, customer_ids
                    )
        calcul_list += self._generate_base_commission()
        calcul_list += self._generate_sponsorship_commission()

        # Calculation commission on refund
        calcul_list += self.calculate_commission_refund()

        if len(calcul_list) > 0:
            self._create_commission_agent(calcul_list)

        # Add tracking
        sync_ok = True
        self._update_synchronization_history(type_sync, comment, sync_ok)

    def action_create_purchase(self, agent_id):
        """ Create purchase """
        if agent_id:
            data = {
                'partner_id': agent_id.id,
                'move_type': "in_invoice",
                'invoice_date': datetime.today(),
            }
            purchase_invoice_id = self.env['account.move'].create(data)
            return purchase_invoice_id
        return False

    @api.model
    def action_generate_purchase_invoice(self):
        """ Create purchase invoice """
        context = dict(self.env.context)

        commission_product = self.env.ref("commission_agent.product_template_commission", False)
        if not commission_product:
            raise UserError(
                _("No commission product configured")
            )
        commission_product_id = self.env['product.product'].search([('product_tmpl_id', '=', commission_product.id)])

        agent_id = False
        for commission in self:
            if agent_id and agent_id != commission.agent_id:
                raise UserError(
                    _("To create a commission invoice, you must select the commissions of a single agent.")
                )
            agent_id = commission.agent_id
            if commission.is_invoiced:
                raise UserError(
                    _("To create a commission invoice, you must select the commissions who don't invoiced.")
                )

        new_purchase_invoice_id = self.action_create_purchase(agent_id.partner_id)
        if new_purchase_invoice_id:
            for commission in self:
                # Create section
                new_line = self.env['account.move.line'].create({
                    'move_id': new_purchase_invoice_id.id,
                    'display_type': 'line_section',
                    'name': commission.name,
                })
                if not commission.edit_mode:
                    for line in commission.commission_agent_calcul_ids:
                        godson_name = ""
                        name = _(
                            "Commission on %s order for %s customer",
                            line.order_id.name,
                            line.partner_id.name,
                        )
                        if line.godson_id:
                            godson_name += _(
                                " - Godson %s",
                                line.godson_id.name
                            )
                        new_line = self.env['account.move.line'].create({
                            'move_id': new_purchase_invoice_id.id,
                            'product_id': commission_product_id.id,
                            'name': name + godson_name,
                            'quantity': 1,
                            'price_unit': line.result,
                        })
                else:
                    new_line = self.env['account.move.line'].create({
                        'move_id': new_purchase_invoice_id.id,
                        'product_id': commission_product_id.id,
                        'name': commission.special_commission,
                        'quantity': 1,
                        'price_unit': commission.amount_force,
                    })

                commission.write({
                    'is_invoiced': True,
                    'purchase_invoice_id': new_purchase_invoice_id.id,
                })

            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'account.move',
                'views': [(self.env.ref('account.view_move_form').id, 'form')],
                'res_id': new_purchase_invoice_id.id,
                'target': 'current',
                'context': context,
            }
