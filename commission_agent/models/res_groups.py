# -*- coding: utf-8 -*-
from odoo import fields, models


class ResGroups(models.Model):
    _inherit = "res.groups"

    is_agent_group = fields.Boolean(string="Is agent group")
