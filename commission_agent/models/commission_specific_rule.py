# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CommissionSpecificRule(models.Model):
    _name = 'commission.specific.rule'
    _rec_name = 'rule_id'
    _description = "Commission specific rule"

    commission_agent_rule_id = fields.Many2one('commission.agent.rule', string="Commission agent rule")
    rule_id = fields.Many2one('commission.agent.rule', string="Rule")
    delta = fields.Integer(
        string="Duration (days)",
        help="Duration between the moment the first rule is applied and the cumulative rules. "
             "Left empty or zero if the duration is indeterminate"
    )
    comment = fields.Char(string="Comment")
    active = fields.Boolean(
        default=True,
        help="By unchecking the active field, you can hide a record without deleting it."
    )
