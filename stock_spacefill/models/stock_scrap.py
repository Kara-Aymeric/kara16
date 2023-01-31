#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright: (c) 2022 irokoo
:license: AGPLv3, see LICENSE for more details

"""
from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    @api.constrains('location_id')
    def _constrains_exported_location_id(self):
        '''
            Check if user can dispose
        '''
        for scrap in self:
            if not self.env.context.get('from_spacefill') and scrap.location_id.warehouse_id \
                and scrap.location_id.warehouse_id.is_exported:
                        raise UserError(_('You are not allowed to scrap for this warehouse !'))
    
    def action_validate(self):
        if self:
           return super(StockScrap, self).action_validate()       
       
#and not self.user_has_groups('stock_spacefill.group_spacefill_connector_users')