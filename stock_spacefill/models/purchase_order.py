#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""


:copyright: (c) 2022 irokoo
:license: AGPLv3, see LICENSE for more details


"""

from odoo import api, fields, models, _
from odoo.addons.stock_spacefill.spacefillpy.api import API as API
from dateutil.relativedelta import relativedelta
from datetime import date, datetime


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        
        pickings = self.env['stock.picking'].search(
           [('origin', '=', self.name)])
        for picking in pickings:
            if picking.picking_type_id.warehouse_id.is_exported and picking.state not in ['done','cancel']:
            #picking.export_order_entry_to_spacefill()
                if not self.env['spacefill.update'].search([('id_to_update','=',picking.id),('is_to_update','=',True)]):
                    self.env['spacefill.update'].create({'id_to_update': picking.id, 'is_to_update': True,'triggered_from':'purchase'})
        
        return res


    
    def write(self, vals):
        res = super(PurchaseOrder, self).write(vals)
        
        if self.name:
            pickings = self.env['stock.picking'].search([('origin', '=', self.name)])
            for picking in pickings:                    
                if picking.picking_type_id.warehouse_id.is_exported and picking.state not in ['done','cancel']:
                    if not self.env['spacefill.update'].search([('id_to_update','=',picking.id),('is_to_update','=',True)]):
                        picking_id = self.env['spacefill.update'].create({'id_to_update': picking.id, 'is_to_update': True,'triggered_from':'purchase'})
        
        return res

    def button_cancel(self):
        res = super(PurchaseOrder, self).button_cancel()
        pickings = self.env['stock.picking'].search([('origin', '=', self.name)])
        for picking in pickings:
            picking.export_order_cancel_to_spacefill()
            picking.update_status_spacefill_with_lot()
        return res