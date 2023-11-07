# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class CommissionRuleCondition(models.Model):
    _name = "commission.rule.condition"
    _rec_name = "operation"
    _order = "id asc"
    _description = "Managing condition about commission rule"

    rule_id = fields.Many2one(
        'commission.agent.rule',
        string="Rule"
    )

    operation = fields.Selection(
        [("count", "Count"), ("sum", "Sum")],
        string="Operation",
        required=True,
    )
    type = fields.Selection(
        [("line", "Line"), ("quantity", "Quantity")],
        string="Type",
        required=True,
    )
    comparison = fields.Selection(
        [("lt", "<"), ("lte", "<="), ("e", "="), ("gte", ">="), ("gt", ">")],
        string="Comparison",
        required=True,
    )
    value = fields.Float(
        string="Value",
        required=True
    )
    logical_operator = fields.Selection(
        [("and", "AND"), ("or", "OR")],
        string="Logical operator"
    )
