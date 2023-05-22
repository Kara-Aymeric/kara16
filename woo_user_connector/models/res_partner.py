# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    agent_commission = fields.Float(
        string="Commission",
        help="When creating a contact from WooCommerce, this commission is recovered for "
             "the assigned to the created contact",
        tracking=True
    )

    agent_discount_commission = fields.Float(
        string="Discount commission",
        help="When creating a contact from WooCommerce, this commission is recovered for "
             "the assigned to the created contact",
        tracking=True
    )
