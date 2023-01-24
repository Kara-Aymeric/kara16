#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""


:copyright: (c) 2022 irokoo
:license: AGPLv3, see LICENSE for more details


"""
import logging
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.stock_spacefill.spacefillpy.api import API as API


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'
    spacefill_pallet= fields.Boolean('Pallet',related='package_type_id.is_spacefill_pallet',store = True)
    spacefill_cardboard_box= fields.Boolean('Box',related='package_type_id.is_spacefill_cardboard_box', store= True)
    
    spacefill_is_package_to_check=fields.Boolean('Spacefill Package to Check', copy=False, compute='_compute_is_package_to_check', default=False)

    spacefill_cardboard_box_weight= fields.Float('Box Weight',compute='_compute_spacefill_cardboard_box_weight')
    spacefill_pallet_weight= fields.Float('Palett Weight',compute='_compute_spacefill_pallet_weight')
    spacefill_cardboard_box_quantity_by_pallet= fields.Integer('Box qty by Pallet', compute='_compute_spacefill_cardboard_box_quantity_by_pallet', store =True, depends=['qty'], default=0)
  
    @api.constrains('product_id','package_type_id')
    def _check_spacefill_pallet(self):
        for productpackaging in self:
            if productpackaging.spacefill_pallet:
                if productpackaging.search_count([('product_id','=',productpackaging.product_id.id),('spacefill_pallet','=',True)]) > 1:
                    raise ValidationError(_('You can not have more than one SpaceFill Pallet for a product'))
            if productpackaging.spacefill_cardboard_box:
                if productpackaging.search_count([('product_id','=',productpackaging.product_id.id),('spacefill_cardboard_box','=',True)]) > 1:
                    raise ValidationError(_('You can not have more than one SpaceFill CardBoard Box for a product'))  



    def create(self, vals):      
      res = super(ProductPackaging, self).create(vals)
      return res
    

    def write(self, vals):
        if self.product_id.is_exported and (self.product_id.purchased_product_qty >0 or self.product_id.sales_count > 0):
            raise ValidationError(_('You can not modify a product that is exported to SpaceFill and that has been sold or purchased'))
        res = super(ProductPackaging, self).write(vals)
        self.product_id.force_to_update= True
        return res
    
    
    def _compute_spacefill_cardboard_box_weight(self):
        for productpackaging in self:
            if productpackaging.spacefill_cardboard_box:
                productpackaging.spacefill_cardboard_box_weight = productpackaging.product_id.weight * productpackaging.qty
            else:
                productpackaging.spacefill_cardboard_box_weight = 0
    
    def _compute_spacefill_pallet_weight(self):
        for productpackaging in self:
            if productpackaging.spacefill_pallet:
                productpackaging.spacefill_pallet_weight = productpackaging.product_id.weight * productpackaging.qty
            else:
                productpackaging.spacefill_pallet_weight = 0
    
   
    def _compute_spacefill_cardboard_box_quantity_by_pallet(self):
        for productpackaging in self:
            if productpackaging.spacefill_pallet:
                box_obj = self.env['product.packaging'].search([('product_id','=',productpackaging.product_id.id),('spacefill_cardboard_box','=',True)],limit=1)
                if box_obj and box_obj.qty > 0 and productpackaging.qty > 0:
                    if int(productpackaging.qty) % int(box_obj.qty) == 0:
                        productpackaging.spacefill_cardboard_box_quantity_by_pallet= int(productpackaging.qty)//int(box_obj.qty)
                    else:
                        productpackaging.spacefill_cardboard_box_quantity_by_pallet = -1
            if productpackaging.spacefill_cardboard_box:
                pal_obj= self.env['product.packaging'].search([('product_id','=',productpackaging.product_id.id),('spacefill_pallet','=',True)],limit=1)
                if pal_obj and pal_obj.qty > 0 and productpackaging.qty > 0:
                    if int(pal_obj.qty) % int(productpackaging.qty) == 0:
                        pal_obj.spacefill_cardboard_box_quantity_by_pallet= int(pal_obj.qty)//int(productpackaging.qty)
                    else:
                        pal_obj.spacefill_cardboard_box_quantity_by_pallet = -1

    def _compute_is_package_to_check(self):
        for package in self:
           package.spacefill_is_package_to_check = False
           if package.spacefill_pallet:
                if self.env['product.packaging'].search_count([('product_id','=',package.product_id.id),('spacefill_cardboard_box','=',True)]) > 0:
                    package.spacefill_is_package_to_check = True 
           33
           if package.spacefill_cardboard_box:
                if self.env['product.packaging'].search_count([('product_id','=',package.product_id.id),('spacefill_pallet','=',True)]) > 0:
                    package.spacefill_is_package_to_check = True                  
          


       



                   
                   
                   
