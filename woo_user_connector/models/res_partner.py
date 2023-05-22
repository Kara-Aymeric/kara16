# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    agent_commission = fields.Float(
        string="Commission",
        tracking=True
    )

    agent_discount_commission = fields.Float(
        string="Discount commission",
        tracking=True
    )
