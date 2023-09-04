# -*- coding: utf-8 -*-


from datetime import timedelta
from collections import defaultdict

from odoo import api, fields, models, _
from odoo.tools import float_compare
from odoo.exceptions import UserError

from math import sin, cos, acos, pi


class SaleOrder(models.Model):
    _inherit = "sale.order"
    def distanceGPS(self,latA, longA, latB, longB):
        """Retourne la distance en mètres entre les 2 points A et B connus grâce à
        leurs coordonnées GPS (en radians).
        """
        # cooordonnées GPS en radians du 1er point (ici, mairie de Tours)
        latA = self.deg2rad(latA) # Nord
        longA = self.deg2rad(longA) # Est
 
    # cooordonnées GPS en radians du 2ème point (ici, mairie de Limoges)
        latB = self.deg2rad(latB) # Nord
        longB = self.deg2rad(longB) # Est
        # Rayon de la terre en mètres (sphère IAG-GRS80)
        RT = 6378137
        # angle en radians entre les 2 points
        S = acos(sin(latA)*sin(latB) + cos(latA)*cos(latB)*cos(abs(longB-longA)))
        # distance entre les 2 points, comptée sur un arc de grand cercle
        return S*RT
    #############################################################################
    def dms2dd(self,d, m, s):
        """Convertit un angle "degrés minutes secondes" en "degrés décimaux"
        """
        return d + m/60 + s/3600
    
    #############################################################################
    def dd2dms(self,dd):
        """Convertit un angle "degrés décimaux" en "degrés minutes secondes"
        """
        d = int(dd)
        x = (dd-d)*60
        m = int(x)
        s = (x-m)*60
        return d, m, s
    
    #############################################################################
    def deg2rad(self,dd):
        """Convertit un angle "degrés décimaux" en "radians"
        """
        return dd/180*pi
    
    #############################################################################
    def rad2deg(self,rd):
        """Convertit un angle "radians" en "degrés décimaux"
        """
        return rd/pi*180
    
    #############################################################################
    #############################################################################
    
    @api.depends('user_id', 'company_id','partner_id','order_line','order_line.product_uom_qty')
    def _compute_warehouse_id(self):
        for order in self:
            if order.state in ['draft'] or not order.ids:
                order.warehouse_id =self.get_the_best_way()

    def get_the_best_way(self):
        max_uom_qty = self.get_max_uom_qty() 
        warehouse_ids = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id), ('max_picking_uom_qty', '>=', max_uom_qty)])        
        list_wh_distance = []
        
        if not self.partner_id.partner_latitude or not self.partner_id.partner_longitude:
            self.partner_id.with_context(force_geo_localize=True).geo_localize()        
        if warehouse_ids:
            for wh_id in warehouse_ids:
                if wh_id.partner_id:
                    if wh_id.partner_id.partner_latitude and wh_id.partner_id.partner_longitude \
                    and self.partner_id.partner_latitude and self.partner_id.partner_longitude:                        
                        distance = self.distanceGPS(self.partner_id.partner_latitude, self.partner_id.partner_longitude, wh_id.partner_id.partner_latitude, wh_id.partner_id.partner_longitude)                        
                        list_wh_distance.append({'id': wh_id.id, 'd': distance})            
            if list_wh_distance:
                best = min(list_wh_distance, key=lambda x: x['d'])
                return best['id']
            else:
                return self.env['ir.default'].with_company(self.company_id.id).get_model_defaults('sale.order').get('warehouse_id')
                
    def get_max_uom_qty(self):
        self.ensure_one()
        max_uom_qty = 0
        for line in self.order_line:
            if line.product_uom_qty > max_uom_qty:
                max_uom_qty = line.product_uom_qty
        return max_uom_qty           
        
  
