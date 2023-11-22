# -*- coding: utf-8 -*-
import logging
import timeit
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class CommissionAgent(models.Model):
    _name = "commission.agent"
    _rec_name = "commission_rule_id"
    _description = "Commission agent generated automatically"

    agent_id = fields.Many2one("res.users", string="Agent", required=True)
    date = fields.Date(string="Commission Date")
    commission_rule_id = fields.Many2one("commission.agent.rule", string="Commission Rule", required=True)
    log_tracking = fields.Char(related="commission_rule_id.log_tracking", readonly=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id, readonly=True
    )
    amount = fields.Monetary(string="Commission amount", compute="_compute_amount", store=True)
    commission_agent_calcul_ids = fields.One2many(
        "commission.agent.calcul", "commission_agent_id", string="Commission agent calcul", required=True
    )

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

    def _get_all_partner_orders(self, partner, agent):
        """ Get all orders for search invoices associated """
        orders = []
        domain_order = [
            ('id', 'in', partner.sale_order_ids.mapped('id')),
            ('user_id', '=', agent.id),
            ('amount_untaxed', '>', 0),
        ]
        order_ids = self.env['sale.order'].search(domain_order)
        for order in order_ids:
            if order.invoice_ids:
                orders.append(order.id)

        return orders

    def _get_invoice_payed(self, agent, invoice_ids, limit):
        """ Get first invoice payed for calculation commission by agent """
        domain_invoice = [
            ('id', 'in', invoice_ids),
            ('state', '=', "posted"),
            ('invoice_user_id', '=', agent.id),
            ('move_type', '=', "out_invoice"),
            ('payment_state', 'in', ["in_payment", "paid"]),
        ]
        invoices = self.env['account.move'].search(domain_invoice, order="invoice_date asc")

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
            print(invoice_date)

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

    def _get_target_invoices(self, partner, agent, start_date, counting_order_new_customer):
        """ Get target invoices for calculation commission """
        all_invoice_list = []
        all_orders = self.env['sale.order'].browse(self._get_all_partner_orders(partner, agent))
        for order in all_orders:
            if order.date_order.date() > start_date:
                all_invoice_list += (
                    self._get_invoice_payed(
                        agent, order.invoice_ids.mapped('id'), counting_order_new_customer
                    )
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
                    commission_calcul.partner_id, agent, start_date, counting_order_new_customer
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
                    invoices = self._get_target_invoices(partner, agent, start_date, counting_order_new_customer)
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
                invoices = self._get_target_invoices(partner, agent, start_date, 10000)
                for invoice in invoices:
                    calcul_ids = self._create_commission_calcul(rule, agent, invoice)
                    calcul_list += calcul_ids.mapped('id')

        return calcul_list

    def _generate_base_commission(self):
        """ Generate base commission for show into calcul """
        calcul_list = []
        commission_base_rule = self.env.ref("commission_agent.commission_base_rule", False)
        if commission_base_rule:
            for order in self.env['sale.order'].search([('dashboard_commission_order', '=', True)]):
                vals = {
                    "agent_id": order.user_id.id,
                    "order_id": order.id,
                    "rule_id": commission_base_rule.id,
                    "result": order.amount_untaxed,
                    "commission_date": order.commission_date,
                }
                # Create commission calcul
                commission_agent_calcul_id = self.env['commission.agent.calcul'].create(vals)
                calcul_list += commission_agent_calcul_id.mapped('id')

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

        if len(calcul_list) > 0:
            self._create_commission_agent(calcul_list)

        # Add tracking
        sync_ok = True
        self._update_synchronization_history(type_sync, comment, sync_ok)
