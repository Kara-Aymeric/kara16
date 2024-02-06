# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    agent_profile = fields.Selection(
        [('ka', "Key Account"), ('d2r', "D2R"), ('other', "Other")],
        string="Agent profile",
        copy=False
    )

    agent_authorize_manual_order = fields.Boolean(
        string="Authorize manual order"
    )
