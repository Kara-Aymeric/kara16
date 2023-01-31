#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright: (c) 2022 irokoo
:license: AGPLv3, see LICENSE for more details

"""
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.constrains('location_id')
    def _constrains_exported_location_id(self):
        '''
            Check if current user is allowed to create inventories for exported locations.
        '''
        for inventory in self:
            if not self.env.context.get('from_spacefill') and inventory.location_id.warehouse_id and inventory.location_id.warehouse_id.is_exported:                   
                            raise UserError(_('You are not allowed to make inventory for this location !'))
# and not self.user_has_groups('stock_spacefill.group_spacefill_connector_users')

    def action_apply_inventory(self):
        '''
            Check if current user is allowed to create inventories for exported locations.
        '''
        for inventory in self:
            if not self.env.context.get('from_spacefill') and inventory.location_id.warehouse_id and inventory.location_id.warehouse_id.is_exported:                   
                            raise UserError(_('You are not allowed to make inventory for this location !'))
        res = super(StockQuant, self).action_apply_inventory()
        return res