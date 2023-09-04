#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright: (c) 2022 irokoo
:license: AGPLv3, see LICENSE for more details

"""
from odoo import api, fields, models, _

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    @api.model_create_multi
    def create(self, vals):       
        res = super(StockPicking, self).create(vals)
        responsible_id = res.picking_type_id.warehouse_id.responsible_id    
        if responsible_id:         
            res.message_post(body="Un nouveau picking %s a été créé. Le responsable est %s." % (res.name, responsible_id.name),
                             subject="Notification de création du Picking",
                             message_type='notification',
                             subtype_xmlid='mail.mt_comment',
                             partner_ids=[responsible_id.partner_id.id])  

        return res


  
    def write(self, vals):       
        res = super(StockPicking, self).write(vals)      
        for picking in self:           
            if 'date_done' in vals:
                responsible_id = picking.picking_type_id.warehouse_id.responsible_id 
                if responsible_id:
                    picking.message_post(body="Le picking %s a été validée. Le responsable est %s." % (self.name, responsible_id.name),
                             subject="Notification de modification du Picking",
                             message_type='notification',
                             subtype_xmlid='mail.mt_comment',
                             partner_ids=[responsible_id.partner_id.id])

        return res
