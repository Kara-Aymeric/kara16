# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    agent_commission_ids = fields.One2many('agent.commission', 'product_template_id', string="Agent commission")
