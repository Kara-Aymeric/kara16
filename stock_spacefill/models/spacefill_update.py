#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""


:copyright: (c) 2022 irokoo
:license: AGPLv3, see LICENSE for more details

"""

from odoo import api, fields, models, _


class SpacefillUpdate(models.Model):
    """Spacefill Auto-Update"""
    _name = "spacefill.update"
    _description = "spacefill.update"


    id_to_update = fields.Char(string='Picking id')
    is_to_update =fields.Boolean(string='Is to update ?',default=False)
    triggered_from = fields.Char(string='Triggered From')
    waiting_for_products_availability = fields.Boolean(string='Waiting for products availability',default=False)

    def update(self):        
        ids_to_treat =self.search([('is_to_update','=',True)])
        for id in ids_to_treat:
            picking = self.env['stock.picking'].search([('id','=',id.id_to_update)])
            if picking.picking_type_id.warehouse_id.is_exported:
                if picking.products_availability_state == 'available' or picking.picking_type_code == 'incoming':
                    picking.action_server_synchronize_order()
                    id.is_to_update = False
                    id.waiting_for_products_availability = False
                else:
                    id.waiting_for_products_availability = True              
    
    @api.model
    def create(self,vals):
        res=super(SpacefillUpdate, self).create(vals)
        if res.is_to_update:
            res.update()
        return res

    def check_availability(self):
        ids_to_treat =self.search([('is_to_update','=',True),('waiting_for_products_availability','=',True)])
        for id in ids_to_treat:
            picking = self.env['stock.picking'].search([('id','=',id.id_to_update)])
            if picking.picking_type_id.warehouse_id.is_exported:
                if picking.products_availability_state == 'available':
                    picking.action_server_synchronize_order()
                    id.is_to_update = False
                    id.waiting_for_products_availability = False