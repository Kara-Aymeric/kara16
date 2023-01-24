#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright: (c) 2022 irokoo
:license: AGPLv3, see LICENSE for more details

"""
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError

class StockPackageType(models.Model):
    _inherit = 'stock.package.type'

    gross_weight = fields.Float(
        'gross weight', help='gross weight shippable in this packaging')
    is_spacefill_cardboard_box = fields.Boolean('SpaceFill CardBoard Box',
        default=False)
    is_spacefill_pallet = fields.Boolean('SpaceFill Pallet', default=False)


    @api.model
    def create(self, vals):        
        if vals.get('is_spacefill_cardboard_box') and vals.get('is_spacefill_pallet'):
            raise UserError(_('You can not have a SpaceFill CardBoard Box and a SpaceFill Pallet at the same time'))
        res = super(StockPackageType, self).create(vals)
        return res
    
  
    def write(self, vals):
        if 'is_spacefill_cardboard_box' in vals and 'is_spacefill_pallet' in vals:
            if vals.get('is_spacefill_cardboard_box') and vals.get('is_spacefill_pallet'):
                raise UserError(_('You can not have a SpaceFill CardBoard Box and a SpaceFill Pallet at the same time'))
        res = super(StockPackageType, self).write(vals)
        return res
