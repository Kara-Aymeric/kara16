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
    is_exported = fields.Boolean(default=False, string='Warehouse managed by SpaceFill',help="If checked, the warehouse will be managed by SpaceFill")
    spacefill_warehouse_account_id = fields.Char(string='Warehouse ID')

    @api.model
    def create(self, vals):
        res = super(StockWarehouse, self).create(vals)
        if res.is_exported:
            res._archive_operation_type()
        return res


    def write(self, vals):
        res = super(StockWarehouse, self).write(vals)
        for warehouse in self:
            if warehouse.is_exported:
                warehouse._archive_operation_type()
        return res    
    def _archive_operation_type(self):        
        operation_type_ids = self.env['stock.picking.type'].search([
                ('warehouse_id','=',self.id),
                ('code','=','internal'),
            ])
        operation_type_ids.write({'active':False})
        operation_type_ids.write({'is_archive_by_default':True})
