# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class CommissionAgentCalcul(models.Model):
    _name = "commission.agent.calcul"
    _rec_name = "commission_agent_id"
    _description = "Model used to managed calcul about commissions"

    commission_agent_id = fields.Many2one("commission.agent", string="Commission agent")
    commission_date = fields.Date(string="Commission date")
    agent_id = fields.Many2one("res.users", string="Agent")
    godson_id = fields.Many2one("res.users", string="Godson")
    order_id = fields.Many2one("sale.order", string="Sale")
    partner_id = fields.Many2one(related="order_id.partner_id", string="Customer", readonly=True)
    currency_id = fields.Many2one(related="order_id.currency_id", string="Currency", readonly=True)
    order_amount_untaxed = fields.Monetary(related="order_id.amount_untaxed", readonly=True)
    rule_id = fields.Many2one(
        "commission.agent.rule", string="Commission Rule"
    )
    result = fields.Float(string="Result")
    commission_freeze = fields.Boolean(
        string="Commission freeze", compute="_compute_commission_freeze", store=True, copy=False
    )

    @api.depends('commission_agent_id', 'commission_agent_id.commission_freeze')
    def _compute_commission_freeze(self):
        """ Compute commission freeze """
        for commission in self:
            commission_freeze = False
            if commission.commission_agent_id and commission.commission_agent_id.commission_freeze:
                commission_freeze = True

            commission.commission_freeze = commission_freeze
