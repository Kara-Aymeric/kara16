# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CommissionSpecificAgent(models.Model):
    _name = 'commission.specific.agent'
    _rec_name = 'agent_id'
    _description = "Commission specific agent"

    rule_id = fields.Many2one('commission.agent.rule', string="Rule")
    agent_id = fields.Many2one('res.users', string="Agent")
    customer_id = fields.Many2one('res.partner', string="Specific customer")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    comment = fields.Char(string="Comment")
    active = fields.Boolean(
        default=True,
        help="By unchecking the active field, you can hide a record without deleting it."
    )
