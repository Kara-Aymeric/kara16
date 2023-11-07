# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CommissionDetailsWizard(models.TransientModel):
    _name = "commission.details.wizard"

    user_id = fields.Many2one("res.users", string="Users")
    commission_rule_id = fields.Many2one("commission.salespeople.rule", string="Rule")
    commission_calcul_ids = fields.Many2many(
        "commission.calcul",
        string="Commissions"
    )
