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
    _description = "Commission agent generated automatically"

    @api.model
    def _default_commission_date(self):
        today = datetime.today()
        last_day_of_month = today + relativedelta(day=31)
        return last_day_of_month.date()

    agent_id = fields.Many2one("res.users", string="Agent")
    date = fields.Date(string="Commission Date", default=lambda self: self._default_commission_date())
    commission_rule_id = fields.Many2one("commission.agent.rule", string="Commission Rule")
    log_tracking = fields.Char(related="commission_rule_id.log_tracking", readonly=True)
    amount = fields.Float(string="Commission Amount")
    commission_agent_calcul_ids = fields.One2many(
        "commission.agent.calcul", "commission_agent_id", string="Commission agent calcul"
    )

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

        print(rules)
        return rules

    def _update_synchronization_history(self, type_sync, comment, sync_ok):
        self.env['synchronization.commission.history'].create({
            'type': "automatic" if type_sync == "automatic" else "manual",
            'name': self.env.user.name,
            'message': comment,
            'sync_ok': sync_ok,
        })

    def _get_active_agent_rule(self, rule):
        """ Get active agent to rule """
        active_agent_rule_ids = self.env['commission.specific.agent'].search([
            ('rule_id', '=', rule.id),
            "|",
            ("start_date", "=", False),
            ("start_date", "<=", fields.Date.today()),
            "|",
            ("end_date", "=", False),
            ("end_date", ">=", fields.Date.today())
        ])
        print(active_agent_rule_ids)
        return active_agent_rule_ids

    def _get_all_partner_orders(self, partner, agent, start_date):
        """ Get all orders for search invoices associated """
        orders = []
        domain_order = [
            ('id', 'in', partner.sale_order_ids.mapped('id')),
            ('user_id', '=', agent.id),
        ]
        if start_date:
            domain_order += [
                ("date_order", ">=", start_date),
            ]
        order_ids = self.env['sale.order'].search(domain_order)
        for order in order_ids:
            if order.invoice_ids:
                orders.append(order.id)

        print(orders)

        return orders

    def _get_all_invoices_payed(self, agent, invoice_ids, start_date, limit):
        """ Get all invoices payed for calculation commission by agent """
        domain_invoice = [
            ('id', 'in', invoice_ids),
            ('state', '=', "posted"),
            ('invoice_user_id', '=', agent.id),
            ('move_type', '=', "out_invoice"),
            ('payment_state', 'in', ["in_payment", "paid"]),
        ]
        if start_date:
            domain_invoice += [
                ('invoice_date', '>=', start_date),
            ]
        invoices = self.env['account.move'].search(domain_invoice, order="invoice_date asc", limit=limit)
        print(invoices)
        return invoices

    def _get_result_commission(self, rule, invoice):
        """ Return amount fixe or percentage result to amount untaxed to invoice """
        if rule.result_type == "amount":
            return rule.result_amount
        elif rule.result_type == "percent":
            return (rule.result_percent / 100) * invoice.amount_untaxed

    def _create_commission_calcul(self, rule, agent, invoice):
        """ Create a commission calcul """
        # amount_untaxed_invoice = invoice.amount_untaxed
        order_id = self.env['sale.order'].search([('name', '=', invoice.invoice_origin)])
        vals = {
            "agent_id": agent,
            "order_id": order_id.id if order_id else False,
            "rule_id": rule.id,
            "result": self._get_result_commission(rule, invoice),
            "commission_date": invoice.commission_date,
        }

        # Create commission calcul
        return self.env['commission.agent.calcul'].create(vals)

    def _generate_commission_new_customer(self, rule, agent, start_date):
        """ Generate commission type equals new customer order """
        calcul_list = []
        commission_date = False
        for partner in self.env['res.partner'].search([('user_id', '=', agent.id)]):
            if partner.sale_order_ids:
                for order in self.env['sale.order'].browse(self._get_all_partner_orders(partner, agent, start_date)):
                    first_invoice = self._get_all_invoices_payed(agent, order.invoice_ids.mapped('id'), start_date, 1)
                    if first_invoice:
                        commission_date = first_invoice.commission_date
                        calcul_ids = self._create_commission_calcul(rule, agent, first_invoice)
                        calcul_list += calcul_ids.mapped('id')
        print(calcul_list)
        if len(calcul_list) > 0:
            vals = {
                'date': commission_date,
                'agent_id': agent.id,
                'commission_rule_id': rule.name,
                'commission_agent_calcul_ids': ([(6, 0, calcul_list)]),
            }
            # Create commission agent (global by rules)
            return self.env['commission.agent'].create(vals)

    def _begin_rule_commission_date(self, rule, agent):
        """ Get begin commission date for calculation commission """
        commission_specific_agent_id = self.env['commission.specific.agent'].search([
            ('rule_id', '=', rule.id),
            ('agent_id', '=', agent.id),
        ])
        if len(commission_specific_agent_id) > 1:
            raise ValidationError(
                _("Impossible to generate commission because rule %s is incorrectly configured on agent list")
            )
        return commission_specific_agent_id.start_date or False

    def calculate_commission(self, type_sync="automatic", comment=""):
        """ Action synchronize """
        rules = self._get_active_rules()
        # invoices = self._get_all_invoices_payed()
        for rule in rules:
            _logger.info(rule.name)
            active_agent_rule_ids = self._get_active_agent_rule(rule)
            apply_on = rule.applies_on
            for agent in active_agent_rule_ids:
                agent_start_date = self._begin_rule_commission_date(rule, agent)
                if apply_on == "new_customer_order":
                    self._generate_commission_new_customer(rule, agent, agent_start_date)
                # elif apply_on == "specific_customer":
                #     pass
                    # self._generate_commission_specific_customer(agent)
                # for invoice in invoices:
                #     commission_date = invoice.commission_date
                #     if rule.applies_on == "first_order":
                #         pass

        # Add tracking
        sync_ok = True
        self._update_synchronization_history(type_sync, comment, sync_ok)

    # Action methods
    def action_open_commission_details(self):
        self.ensure_one()
        ctx = {
            'default_model': 'commission.agent',
            'default_res_id': self.ids[0],
            'default_user_id': self.agent_id.id,
            'src_model': 'commission.agent',
            'default_commission_rule_id': self.commission_rule_id.id,
            # 'default_commission_calcul_ids': self.env["commission.calcul"].search([
            #     ('salesperson_id', '=', self.salesperson_id.id),
            #     ('commission_rule_id', '=', self.commission_rule_id.id),
            #     ('commission_date', '=', self.commission_date),
            #     ('amount', '!=', 0.00)]).ids,
        }
        return {
            'name': self.commission_rule_id.name,
            'res_model': 'commission.detail.wizard',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'view_id': self.env.ref('commission_agent.commission_detail_wizard_form_view').id,
            'target': 'new',
            'context': ctx,
        }

    # def _define_domain_for_sale_order(self, rule, domain):
    #     if rule.applies_to == "total_invoice_paid":
    #         domain += [
    #             ("invoice_ids", "!=", False),
    #             ("invoice_ids.date_for_commission", "!=", False),
    #             ("invoice_ids.state", "!=", "cancel")
    #         ]
    #     elif rule.applies_to == "specific_source":
    #         source_ids = [source.id for source in rule.specific_source_id]
    #         domain += [("source_id", "in", source_ids)]
    #     elif rule.applies_to == "specific_product":
    #         product_ids = [product.id for product in rule.specific_product_id]
    #         domain += [("order_line.product_template_id", "in", product_ids)]
    #     if rule.salesperson_ids:
    #         domain += [
    #             "|",
    #             ("user_id", "in", rule.salesperson_ids.ids),
    #             ("support_technician_id", "in", rule.salesperson_ids.ids),
    #         ]
    #     return domain
    #
    # def calculate_commission(self, manual=False, comment=""):
    #     sync_date_start = fields.Datetime.now()
    #     error = ""
    #     rules = self.env["commission.salespeople.rule"].search([
    #         "|",
    #         ("expiration_date", "=", False),
    #         ("expiration_date", ">=", fields.Date.today()),
    #         "|",
    #         ("start_date", "=", False),
    #         ("start_date", "<=", fields.Date.today()),
    #     ])
    #     for rule in rules:
    #         t1 = timeit.default_timer()
    #         _logger.info(rule.name)
    #         domain = [("state", "=", "sale"), ("user_id", "!=", False)]
    #
    #         if rule.is_cumulative:
    #             for cumulative_rule in rule.cumulative_with_ids:
    #                 domain = self._define_domain_for_sale_order(rule=cumulative_rule, domain=domain)
    #         domain = self._define_domain_for_sale_order(rule=rule, domain=domain)
    #
    #         if rule.applies_to in ("total_invoice", "total_invoice_paid", "specific_product", "specific_source"):
    #             domain_without_payroll = domain + [("payroll_deduction", "=", False)]
    #             if rule.applies_to == "total_invoice_paid":
    #                 self.create_commissions(rule=rule, domain=domain_without_payroll, payroll_deduction=False,
    #                                         check_invoice_paid=True)
    #             self.create_commissions(rule=rule, domain=domain_without_payroll, payroll_deduction=False,
    #                                     check_invoice_paid=False)
    #
    #             domain_with_payroll = domain + [("payroll_deduction", "!=", False)]
    #             if rule.applies_to == "total_invoice_paid":
    #                 self.create_commissions(rule=rule, domain=domain_with_payroll, payroll_deduction=False,
    #                                         check_invoice_paid=True)
    #             self.create_commissions(rule=rule, domain=domain_with_payroll, payroll_deduction=True,
    #                                     check_invoice_paid=False)
    #             self.calculate_commission_for_employees(rule)
    #         else:
    #             error = _("Not Implemented yet.")
    #         _logger.info(f"{rule.name} : calculation done after {str(timeit.default_timer() - t1)}")
    #     _logger.info("Calculate Commission DONE!")
    #     self.env["synchronisation_commission_history"].sudo().create({
    #         "user_id": self.env.user.id,
    #         "sync_datetime_start": sync_date_start,
    #         "sync_datetime_end": fields.Datetime.now(),
    #         "comment": comment,
    #         "manual": manual,
    #         "result": _("Synchronized") if not error else error
    #     })
    #
    #     if error:
    #         raise ValidationError(error)
    #
    #     return True
    #
    # def create_commissions(self, rule, domain, payroll_deduction=False, check_invoice_paid=False):
    #     commissions = self.env["commission.calcul"].search([
    #         ("commission_rule_id", "=", rule.id),
    #         ("payroll_deduction", "=", payroll_deduction),
    #     ])
    #     if commissions:
    #         domain += [("id", "not in", [commission.order_id.id for commission in commissions])]
    #
    #     count = any(condition.operation == "count" for condition in rule.condition_ids)
    #     orders = self.env["sale.order"].search(domain)
    #
    #     for order in orders:
    #         if not check_invoice_paid:
    #             self.check_every_order(count, order, payroll_deduction, rule)
    #         else:
    #             self.check_every_order_line(order, payroll_deduction, rule)
    #
    # def _get_amount_of_invoice(self, move, rule):
    #     subtotal_lines_with_discount = 0.00
    #
    #     if rule.has_discount_condition:
    #         subtotal_lines_with_discount = round(
    #             sum(line.price_subtotal for line in move.sale_order_id.order_line.filtered(
    #                 lambda sol: sol.discount > (rule.discount_threshold * 100))), 2)
    #         subtotal_lines_without_discount = sum(
    #             line.price_subtotal for line in move.sale_order_id.order_line.filtered(
    #                 lambda sol: sol.discount <= (rule.discount_threshold * 100))
    #         )
    #     else:
    #         subtotal_lines_without_discount = sum(line.price_subtotal for line in move.sale_order_id.order_line)
    #     return subtotal_lines_without_discount, subtotal_lines_with_discount
    #
    # def check_every_order_line(self, order, payroll_deduction, rule):
    #     for move in order.invoice_ids:
    #         has_follower_technician = False
    #         has_discount_condition = False
    #         base_to_calcul_commission = 0.00
    #
    #         subtotal_lines_without_discount, subtotal_lines_with_discount = self._get_amount_of_invoice(move=move,
    #                                                                                                     rule=rule)
    #         sale_order_base_to_calcul = subtotal_lines_with_discount + subtotal_lines_without_discount
    #
    #         if rule.follower_technician_restriction:
    #             base_to_calcul_commission = sale_order_base_to_calcul / 2 if move.technician_id else (
    #                 sale_order_base_to_calcul)
    #             if move.technician_id:
    #                 has_follower_technician = True
    #
    #         if not has_follower_technician:
    #             base_to_calcul_commission = sale_order_base_to_calcul
    #
    #         if move.move_type == "out_refund":
    #             base_to_calcul_commission = base_to_calcul_commission * -1
    #             payroll_deduction = True
    #
    #         rule_id = self.get_default_rule_for_agent(user_id=move.invoice_user_id.id)
    #         if rule.result_type == "percent":
    #             if rule_id is not None:
    #                 if rule_id.has_discount_condition and subtotal_lines_with_discount:
    #                     commission_calculated = round(base_to_calcul_commission * rule_id.discount_commission_result, 2)
    #                     has_discount_condition = True
    #                 else:
    #                     commission_calculated = round(base_to_calcul_commission * rule_id.result_percent, 2)
    #             else:
    #                 if rule.has_discount_condition and subtotal_lines_with_discount:
    #                     commission_calculated = round(base_to_calcul_commission * rule.discount_commission_result, 2)
    #                     has_discount_condition = True
    #                 else:
    #                     commission_calculated = round(base_to_calcul_commission * rule.result_percent, 2)
    #         else:
    #             commission_calculated = base_to_calcul_commission
    #
    #         last_date_of_month = move.date_for_commission if not payroll_deduction else order.payroll_deduction
    #         vals = {
    #             "salesperson_id": move.invoice_user_id.id,
    #             "order_id": order.id,
    #             "commission_rule_id": rule_id and rule_id.id or rule.id,
    #             "amount": commission_calculated,
    #             "commission_date": last_date_of_month,
    #             "payroll_deduction": payroll_deduction,
    #             "has_discount_condition": has_discount_condition,
    #             "has_follower_technician": has_follower_technician,
    #         }
    #
    #         if commission_calculated and last_date_of_month:
    #             calcul = self.env["commission.calcul"].search([
    #                 ("order_id", "=", order.id),
    #                 ("commission_rule_id", "=", rule_id and rule_id.id or rule.id),
    #                 ("salesperson_id", "=", move.invoice_user_id.id),
    #                 ("commission_date", "=", last_date_of_month),
    #                 ("payroll_deduction", "=", payroll_deduction),
    #             ])
    #
    #             if not calcul:
    #                 self.env["commission.calcul"].create(vals)
    #                 if has_follower_technician:
    #                     is_already_done = False
    #                     same_type_rule = True
    #                     vals["commission_rule_id"] = rule.id
    #                     vals["salesperson_id"] = move.technician_id.id
    #                     vals["amount"] = round(base_to_calcul_commission * (
    #                             rule.specific_percent_for_follower_technician or rule.result_percent), 2)
    #                     rule_id = self.get_default_rule_for_agent(user_id=move.technician_id.id)
    #                     if rule_id is not None:
    #                         is_already_done = self.env["commission.calcul"].search_count([
    #                             ('order_id', '=', order.id),
    #                             ('commission_rule_id', '=', rule_id.id)
    #                         ])
    #                         # Si l'employé technicien à une règle par défaut, nous devons recalculer la commission
    #                         if rule_id.applies_to != rule.applies_to:
    #                             same_type_rule = False
    #                             commission_calculated = round(base_to_calcul_commission * rule_id.result_percent, 2)
    #                         vals["commission_rule_id"] = rule_id.id
    #                         vals["amount"] = commission_calculated
    #                     if not calcul and not is_already_done and same_type_rule:
    #                         self.env["commission.calcul"].create(vals)
    #
    # def check_every_order(self, count, order, payroll_deduction, rule):
    #     has_follower_technician = False
    #     has_discount_condition = False
    #     commission_calculated = 0.00
    #
    #     if rule.follower_technician_restriction:
    #         if count:
    #             commission_calculated = 0.5 if order.support_technician_id else 1
    #         else:
    #             commission_calculated = (
    #                 order.amount_untaxed / 2
    #                 if order.support_technician_id
    #                 else order.amount_untaxed
    #             )
    #         if order.support_technician_id:
    #             has_follower_technician = True
    #
    #     if rule.has_discount_condition:
    #         if any(line.discount > (rule.discount_threshold * 100) for line in order.order_line):
    #             commission_calculated = round(commission_calculated * rule.discount_commission_result, 2)
    #             has_discount_condition = True
    #
    #     if payroll_deduction:
    #         commission_calculated *= -1
    #
    #     if not payroll_deduction:
    #         last_date_of_month = order.date_order + relativedelta(day=31)
    #     else:
    #         last_date_of_month = order.payroll_deduction
    #
    #     rule_id = self.get_default_rule_for_agent(user_id=order.user_id.id)
    #     vals = {
    #         "salesperson_id": order.user_id and order.user_id.id,
    #         "order_id": order.id,
    #         "commission_rule_id": rule_id and rule_id.id or rule.id,
    #         "amount": commission_calculated,
    #         "commission_date": last_date_of_month,
    #         "payroll_deduction": payroll_deduction,
    #         "has_discount_condition": has_discount_condition,
    #         "has_follower_technician": has_follower_technician,
    #     }
    #
    #     if vals and order.user_id:
    #         same_type_rule = True
    #         if order.user_id in rule.salesperson_ids:
    #             if rule_id is not None and rule_id.applies_to != rule.applies_to:
    #                 same_type_rule = False
    #             if same_type_rule:
    #                 self.env["commission.calcul"].create(vals)
    #         if has_follower_technician:
    #             is_already_done = False
    #             same_type_rule = True
    #             vals["commission_rule_id"] = rule.id
    #             vals["salesperson_id"] = order.support_technician_id.id
    #             rule_id = self.get_default_rule_for_agent(user_id=order.support_technician_id.id)
    #             if rule_id is not None:
    #                 is_already_done = self.env["commission.calcul"].search_count([
    #                     ('order_id', '=', order.id),
    #                     ('commission_rule_id', '=', rule_id.id)
    #                 ])
    #                 if rule_id.applies_to != rule.applies_to:
    #                     same_type_rule = False
    #                 vals["commission_rule_id"] = rule_id.id
    #                 vals["amount"] = commission_calculated
    #             if not is_already_done and same_type_rule:
    #                 self.env["commission.calcul"].create(vals)
    #
    # def calculate_commission_for_employees(self, rule):
    #     query = """
    #             select sum(amount) as total, salesperson_id, commission_date
    #             from commission_calcul
    #             where commission_rule_id = %s
    #             group by salesperson_id, commission_date
    #         """
    #
    #     params = ""
    #     for condition in rule.condition_ids:
    #         if not params:
    #             params = " HAVING "
    #         params += "SUM(amount) "
    #         params += (
    #                 " "
    #                 + dict(
    #             self.env["commission.salespeople.condition"]
    #             ._fields["comparison"]
    #             .selection
    #         ).get(condition.comparison)
    #                 + " "
    #         )
    #         params += str(condition.value)
    #         if condition.logical_operator:
    #             params += f" {condition.logical_operator} "
    #
    #     self.env.cr.execute(query + params, [rule.id])
    #     rows = self.env.cr.dictfetchall()
    #     for row in rows:
    #         res_amount = rule.result_amount if rule.result_type == "amount" else row["total"]
    #
    #         if res_amount:
    #             commission = self.env["commission"].search([
    #                 ("salesperson_id", "=", row["salesperson_id"]),
    #                 ("commission_date", "=", row["commission_date"]),
    #                 ("commission_rule_id", "=", rule.id),
    #             ])
    #
    #             vals = {
    #                 "salesperson_id": row["salesperson_id"],
    #                 "commission_date": row["commission_date"],
    #                 "commission_rule_id": rule.id,
    #                 "amount": res_amount,
    #             }
    #
    #             if not commission:
    #                 self.create(vals)
    #             else:
    #                 commission.write(vals)
    #
# Optionally, you may define other methods or classes here as needed.