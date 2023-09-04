#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright: (c) 2022 irokoo
:license: AGPLv3, see LICENSE for more details

"""
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"    
    
    max_picking_uom_qty = fields.Integer(string='Max picking qty',default=100,help="Max picking qty")
    responsible_id = fields.Many2one('res.users', string='Responsible',help="Responsible")
    


