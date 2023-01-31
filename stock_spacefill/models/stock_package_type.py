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
        if 'is_spacefill_cardboard_box' in vals or 'is_spacefill_pallet' in vals:
            for rec in self:
                if rec.is_spacefill_pallet or rec.is_spacefill_cardboard_box:
                    raise UserError(_('You can not modify SpaceFill CardBoard Box or a SpaceFill Pallet when products are exported'))
        # propagation to products        
        res = super(StockPackageType, self).write(vals)
        """
        for rec in self:
            if rec.is_spacefill_cardboard_box or rec.is_spacefill_pallet:
                for products in self.env['product.product'].search([('is_exported', '=', True)]):
                    for product in products:
                        for package in product.packaging_ids:
                            if package.package_type_id.id == rec.id:
                                product.force_to_update= True
        """
        return res
    def unlink(self):
        for rec in self:
            if rec.is_spacefill_cardboard_box or rec.is_spacefill_pallet:
                raise UserError(_('You can not delete a SpaceFill CardBoard Box or a SpaceFill Pallet'))
        res = super(StockPackageType, self).unlink()
        return res