# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class CommissionAgentRule(models.Model):
    _name = "commission.agent.rule"
    _description = "Managing commission rules"

    name = fields.Char(string="Rule name", tracking=True)
    sequence = fields.Integer(string="Sequence", default=100)
    description = fields.Char(string="Description")
    log_tracking = fields.Char(
        string="Log", help="Shortcut that appear in the calculation", tracking=True
    )
    start_date = fields.Date(string="Start Date", tracking=True)
    expiration_date = fields.Date(string="Expiration Date", tracking=True)
    is_expired = fields.Boolean(
        string="Is expired", copy=False, compute="_compute_is_expired", store=True, tracking=True
    )

    # Applied to
    for_all_agent = fields.Boolean(string="For all agent ?", copy=False)
    agent_ids = fields.Many2many("res.users", string="Agents", copy=False, tracking=True)
    applies_to = fields.Selection(
        [
            ("new_customer", "New customer"),
            ("new_ka_customer", "New key account customer"),
            ("specific_customer", "Specific customer"),
            ("specific_product", "Specific product"),
            ("total_amount_order", "Total amount order (HT)"),
            ("total_amount_invoice", "Total amount invoice (HT)"),
        ],
        string="Applies on",
        tracking=True
    )

    # Applied to - Specific product
    specific_product_id = fields.Many2many(
        "product.template", string="Specific Product", copy=False
    )

    # Cumulative rules
    is_cumulative = fields.Boolean(string="Is Cumulative", tracking=True)
    cumulative_with_ids = fields.One2many(
        'commission.specific.rule', 'commission_agent_rule_id', string="Cumulative with", copy=False
    )

    # Conditions
    condition_rule_ids = fields.One2many(
        "commission.rule.condition",
        "rule_id",
        string="Condition",
        copy=False,
    )

    # Conditions - Discount
    has_discount_condition = fields.Boolean(string="Has discount condition", tracking=True)
    discount_limit = fields.Float(string="Discount limit", tracking=True)
    discount_result_type = fields.Selection(
        [("amount", "Amount"), ("percent", "Percentage")], string="Type of result", tracking=True
    )
    discount_result_amount = fields.Monetary(string="Amount", tracking=True)
    discount_result_percent = fields.Float(string="Percentage", tracking=True)

    # Result
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id, readonly=True
    )
    result_type = fields.Selection(
        [("amount", "Amount"), ("percent", "Percentage")], string="Type of result", tracking=True
    )
    result_amount = fields.Monetary(string="Amount", tracking=True)
    result_percent = fields.Float(string="Percentage", tracking=True)

    active = fields.Boolean(string="Active", default=True, tracking=True)

    # compute and search fields, in the same order of fields declaration
    @api.depends("expiration_date")
    def _compute_is_expired(self):
        """ Compute is expired """
        for rule in self:
            is_expired = False
            if rule.expiration_date:
                if fields.Date.today() > rule.expiration_date:
                    is_expired = True
            rule.is_expired = is_expired

    @api.onchange("for_all_agent")
    def _onchange_for_all_agent(self):
        """ Onchange for simplify add agent to rule """
        if self.for_all_agent:
            res_groups = self.env["res.groups"].search(
                [("is_agent_group", "=", True)]
            )
            self.agent_ids = [(6, 0, res_groups.users.ids)]
        else:
            self.agent_ids = [(6, 0, ())]

    @api.onchange("has_discount_condition")
    def _onchange_has_discount_condition(self):
        """ Onchange for clear fields if not has discount condition """
        if not self.has_discount_condition:
            self.write({
                'discount_limit': False,
                'discount_result_type': False,
                'discount_result_amount': False,
                'discount_result_percent': False,
            })

    @api.onchange("discount_result_type")
    def _onchange_discount_result_type(self):
        """ Onchange discount result type for clear result value depend discount result type """
        if self.discount_result_type == "amount":
            self.discount_result_percent = False
        elif self.discount_result_type == "percent":
            self.discount_result_amount = False

    @api.onchange("result_type")
    def _onchange_result_type(self):
        """ Onchange result type for clear result value depend result type """
        if self.result_type == "amount":
            self.result_percent = False
        elif self.result_type == "percent":
            self.result_amount = False
