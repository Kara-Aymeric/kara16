#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright: (c) 2022 irokoo
:license: AGPLv3, see LICENSE for more details

"""

from odoo import models, fields, api


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

def write(self,vals):
    res=super(StockMoveLine, self).write(vals)
    
    if self.picking_id.picking_type_id.warehouse_id.is_exported and self.env.context.get('_send_on_write')!='NO' and self.picking_id.state not in ['done','cancel']:
        if not self.env['spacefill.update'].search([('id_to_update','=',self.picking_id.id),('is_to_update','=',True)]):
            self.env['spacefill.update'].create({'id_to_update':self.picking_id.id,'is_to_update':True,'triggered_from':'stock_move_line'})
        
    return res