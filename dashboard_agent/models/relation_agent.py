# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class RelationAgent(models.Model):
    _name = 'relation.agent'

    name = fields.Char(
        string="Name",
        required="True"
    )
    principal_agent_id = fields.Many2one(
        'res.users',
        string="Principal agent",
        domain=lambda self: [('groups_id', 'in', self.env.ref('dashboard_agent.group_principal_agent').id)]
    )
    agent_ids = fields.Many2many(
        'res.users',
        string="Agents",
        domain=lambda self: [('groups_id', 'in', self.env.ref('dashboard_agent.group_external_agent').id)]
    )
    active = fields.Boolean(
        default=True,
        help="By unchecking the active field, you can hide a record without deleting it."
    )
