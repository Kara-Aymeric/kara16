# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class CommissionAgentRule(models.Model):
    _name = "commission.agent.rule"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Managing commission rules"

    name = fields.Char(string="Rule name", tracking=True)
    sequence = fields.Integer(string="Sequence", default=100)
    description = fields.Text(string="Description")
    log_tracking = fields.Char(
        string="Log", help="Shortcut that appear in the calculation", tracking=True
    )
    start_date = fields.Date(string="Start Date", tracking=True)
    expiration_date = fields.Date(string="Expiration Date", tracking=True)
    is_expired = fields.Boolean(
        string="Is expired", copy=False, compute="_compute_is_expired", store=True, tracking=True
    )
    is_sponsorship_rule = fields.Boolean(string="Is sponsorship rule")
    total_recovery_on_refund = fields.Boolean(
        string="Total recovery on refund",
        help="When this option is active, a total recovery of the commission paid is made if the refund is total "
             "(does not work for partial refund)"
    )
    # Applied to
    agent_ids = fields.One2many(
        'commission.specific.agent', 'rule_id', string="Agents", copy=False
    )
    # applies_on = fields.Selection(
    #     [
    #         ("first_order", "First order new customer"),
    #         ("first_order_ka", "First order new key account customer"),
    #         ("specific_brand", "Specific brand"),
    #         ("specific_product", "Specific product"),
    #         ("specific_customer", "Specific customer"),
    #         ("total_amount_cashing", "Total amount cashing (HT)"),
    #     ],
    #     string="Applies on",
    #     tracking=True
    # )
    applies_on = fields.Selection(
        [
            ("new_customer_order", "New customer order"),
            ("specific_customer", "Specific customer"),
        ],
        string="Applies on",
        tracking=True
    )

    # Applied to - Specific customer
    is_specific_customer_rule = fields.Boolean(
        string="Is specific customer rule",
        compute="_compute_is_specific_customer_rule",
    )

    # Applied to - Specific product
    specific_product_id = fields.Many2many(
        "product.template", string="Specific Product", copy=False
    )

    # Applied to - Specific product
    specific_brand_id = fields.Many2many(
        "agorane.product.brand", string="Specific brand", copy=False
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

    is_not_calculation_sponsorship = fields.Boolean(
        string="No sponsorship",
        help="If this option is active, the orders found in this rule are not taken into account in the calculation "
             "of commissions concerning the sponsorship rule",
        tracking=True
    )

    active = fields.Boolean(string="Active", default=True, tracking=True)

    @api.depends('applies_on')
    def _compute_is_specific_customer_rule(self):
        """ If specific customer rule, open other option into form view """
        for rule in self:
            is_specific_customer_rule = False
            if rule.applies_on == "specific_customer":
                is_specific_customer_rule = True

            rule.is_specific_customer_rule = is_specific_customer_rule

    @api.depends("expiration_date")
    def _compute_is_expired(self):
        """ Compute is expired """
        for rule in self:
            is_expired = False
            if rule.expiration_date:
                if fields.Date.today() > rule.expiration_date:
                    is_expired = True
            rule.is_expired = is_expired

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

    @api.onchange("condition_rule_ids")
    def _onchange_condition_rule_ids(self):
        return {
            'warning': {
                'title': _("Alert on condition"),
                'message': _("Please, conditions are important in calculating commissions. "
                             "Please check the data you add carefully.")
            },
        }
