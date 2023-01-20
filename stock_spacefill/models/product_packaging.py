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
    spacefill_palett= fields.Boolean('SpaceFill Palett',related='package_type_id.is_spacefill_pallet',store=True)
    spacefill_cardboard_box= fields.Boolean('SpaceFill CardBoard Box',related='package_type_id.is_spacefill_cardboard_box',store=True)


    def create(self, vals):
       for productpackaging in self:
              if productpackaging.search_count([('product_id','=',vals.get('product_id')),('spacefill_palett','=',True)]) == 1:
                raise UserError(_('You can not have more than one SpaceFill Palett for a product'))
              if productpackaging.search_count([('product_id','=',vals.get('product_id')),('spacefill_cardboard_box','=',True)]) == 1:
                raise UserError(_('You can not have more than one SpaceFill CardBoard Box for a product'))
       res = super(ProductPackaging, self).create(vals)
       return res
    

    def write(self, vals):
           
        res = super(ProductPackaging, self).write(vals)
        return res
    