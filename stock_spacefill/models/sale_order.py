#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""


:copyright: (c) 2022 irokoo
:license: AGPLv3, see LICENSE for more details


"""

from odoo import api, fields, models, _
from odoo.addons.stock_spacefill.spacefillpy.api import API as API
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
    _inherit = "sale.order" 

    def action_confirm(self):
        res= super(SaleOrder, self).action_confirm() 
        for order in self:
            pickings = self.env['stock.picking'].search([('origin','=',order.name)])
            for picking in pickings:
                if picking.picking_type_id.warehouse_id.is_exported and picking.state not in ['done','cancel']:
                    #picking.export_order_exit_to_spacefill()
                    if not self.env['spacefill.update'].search([('id_to_update','=',picking.id),('is_to_update','=',True)]):
                        self.env['spacefill.update'].create({'id_to_update': picking.id, 'is_to_update': True,'triggered_from':'sale'})
        return res

    def update_exit(self):
        pickings = self.env['stock.picking'].search(
           [('origin', '=', self.name)])
        for picking in pickings:
            if picking.picking_type_id.warehouse_id.is_exported:
                picking.export_order_exit_to_spacefill()
   
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if self.name:
            pickings = self.env['stock.picking'].search([('origin', '=', self.name)])  
            for picking in pickings:                  
                if picking.picking_type_id.warehouse_id.is_exported and picking.state not in ['done','cancel']:
                    if not self.env['spacefill.update'].search([('id_to_update','=',picking.id),('is_to_update','=',True)]):
                        picking_id = self.env['spacefill.update'].create({'id_to_update': picking.id, 'is_to_update': True,'triggered_from':'sale'})                 
                #picking.export_order_entry_to_spacefill()
        return res
    def button_cancel(self):
        res = super(SaleOrder, self).button_cancel()
        pickings = self.env['stock.picking'].search([('origin', '=', self.name)])
        for picking in pickings:
            picking.export_order_cancel_to_spacefill()
            picking.update_status_spacefill_with_lot()
        return res
    