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

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_exported=fields.Boolean('Spacefill Exported Product', copy=False)
    item_spacefill_id=fields.Char('Spacefill Product ID', copy=False)
    force_to_update = fields.Boolean('Force to update', copy=False, default=False)


    def create_spacefill_variant(self,instance,vals):
        """
        Create or update a variant in spacefill

        Args:
            instance (obj): instance of spacefill
            vals (dict): values of the variant
        """
        item_url = 'logistic_management/master_items/'

        if not self.item_spacefill_id and self._constrains_mandatory_fields():
            res= instance.create(instance.url+item_url, vals)
            if isinstance(res,dict):
                self.message_post(
                            body=_('Product Created in Spacefill with id %s') % (res.get('id')),
                                                )
                self.write({'item_spacefill_id' : res.get('id')})
                self.write({'is_exported': True})
            else:
                raise ValidationError(_('Error from API : %s') % (res))
        else:
            # update
            try:
                
                res= instance.update(instance.url+item_url+self.item_spacefill_id+"/", vals)
                if isinstance(res,dict):
                    self.message_post(
                                body=_('Product Updated in Spacefill with id %s') % (res.get('id')),
                                                )
                else:
                    raise ValidationError(_('Product : %s - Error from API : %s') % (self.name,res))
            except Exception as e:
                raise ValidationError(_('Error while updating item in Spacefill : %s') % (e))
                       
    def export_product_in_spacefill(self):
        """
            Export product in spacefill
        """
        for product in self:
                instance, setup = product.get_instance_spacefill()
                spacefill_mapping= {
                    "shipper_account_id": setup.spacefill_erp_account_id,
                    "item_reference": None,
                    "designation": product.name,
                    "cardboard_box_quantity_by_pallet": None,
                    "each_barcode_type": "EAN",
                    "each_barcode": product.barcode if product.barcode else None,
                    "cardboard_box_barcode_type": "EAN",
                    "cardboard_box_barcode": None,
                    "pallet_barcode_type": "EAN",
                    "pallet_barcode": None,
                    "each_quantity_by_cardboard_box": None,
                    "each_quantity_by_pallet":None,
                    "each_is_stackable": "true",
                    "cardboard_box_is_stackable": "false",
                    "pallet_is_stackable": "false",
                    "each_width_in_cm": None,
                    "each_length_in_cm": None,
                    "each_height_in_cm": None,
                    "each_volume_in_cm3": None,
                    "cardboard_box_width_in_cm": None,
                    "cardboard_box_length_in_cm": None,
                    "cardboard_box_height_in_cm": None,
                    "cardboard_box_volume_in_cm3": None,
                    "pallet_width_in_cm": None,
                    "pallet_length_in_cm": None,
                    "pallet_height_in_cm": None,
                    "pallet_gross_weight_in_kg": None,
                    "pallet_net_weight_in_kg": None,
                    "cardboard_box_gross_weight_in_kg": None,
                    "cardboard_box_net_weight_in_kg": None,
                    "each_gross_weight_in_kg": product.weight if product.weight else None,
                    "each_net_weight_in_kg": product.weight if product.weight else None,
                    "edi_erp_id": product.id,
                    "edi_wms_id": None,
                    "edi_tms_id": None,
                    "transfered_to_erp_at": None,
                    "transfered_to_wms_at": None,
                    "transfered_to_tms_at": None,
                    }
                vals = product.prepare_dict_vals(spacefill_mapping)
                vals = product.get_values(vals)
                product.create_spacefill_variant(instance,vals)

    def get_instance_spacefill(self):
        setup = self.env['spacefill.config'].search([('company_id', '=',self.env.company.id)], limit=1)
        if not setup:
            raise ValidationError(_('Spacefill configuration is not set for this company'))
        if len(self.env['res.company'].search([])) >1 and self.company_id.id != self.env.company.id:
            raise ValidationError (_('Cannot export a product available for several company, you need to set a company on the product & on the product packagings :%s') % (self.name))
        instance = API(setup.spacefill_api_url,
                       setup.spacefill_shipper_token)       
        return instance,setup

    def prepare_dict_vals(self, spacefill_mapping):
        spacefill_cardboard_box = False
        spacefill_pallet = False
        if self.packaging_ids:
            for package in self.packaging_ids:
                if package.package_type_id.is_spacefill_cardboard_box:
                    if spacefill_cardboard_box:
                        raise ValidationError(_('You can not have more than one cardboard box type'))
                    spacefill_cardboard_box = True
                    obj_cardbox= package

                elif package.package_type_id.is_spacefill_pallet:
                    if spacefill_pallet:
                        raise ValidationError(_('You can not have more than one pallet type'))
                    spacefill_pallet = True
                    obj_pal = package

            
            if spacefill_pallet:
                if spacefill_cardboard_box:
                    if obj_pal.qty % obj_cardbox.qty == 0:
                        spacefill_mapping["cardboard_box_quantity_by_pallet"] = int(obj_pal.qty//obj_cardbox.qty)
                    else:
                        self.message_post(
                                                body=_('Cardboard box quantity by pallet is not an integer'),
                                                )
                        raise ValidationError (_('Cannot export a product with a pallet quantity not divisible by the cardboard box quantity, correct the packaging configuration of the product %s') % (self.name))               
                    
                else:
                    spacefill_mapping["each_quantity_by_pallet"] = int(obj_pal.qty)

                spacefill_mapping["pallet_barcode"] = obj_pal.barcode if obj_pal.barcode else None
                spacefill_mapping["pallet_width_in_cm"] = obj_pal.package_type_id.width if obj_pal.package_type_id.width else None
                spacefill_mapping["pallet_length_in_cm"] = obj_pal.package_type_id.packaging_length if obj_pal.package_type_id.packaging_length else None
                spacefill_mapping["pallet_height_in_cm"] = obj_pal.package_type_id.height if obj_pal.package_type_id.height else None
                spacefill_mapping["pallet_gross_weight_in_kg"] = int(obj_pal.spacefill_pallet_weight) if obj_pal.spacefill_pallet_weight > 1 else None # to prevent API error
                spacefill_mapping["pallet_net_weight_in_kg"] = int(obj_pal.spacefill_pallet_weight) if obj_pal.spacefill_pallet_weight > 1 else None

            if spacefill_cardboard_box:
                # remplir les détails cardboard box
                #cardBoardBox = values["cardBoardBox"]
                spacefill_mapping["each_quantity_by_cardboard_box"] = int(obj_cardbox.qty)
                spacefill_mapping["cardboard_box_barcode"] = obj_cardbox.barcode if obj_cardbox.barcode else None
                spacefill_mapping["cardboard_box_width_in_cm"] = obj_cardbox.package_type_id.width if obj_cardbox.package_type_id.width else None
                spacefill_mapping["cardboard_box_length_in_cm"] = obj_cardbox.package_type_id.packaging_length if obj_cardbox.package_type_id.packaging_length else None
                spacefill_mapping["cardboard_box_height_in_cm"] = obj_cardbox.package_type_id.height  if obj_cardbox.package_type_id.height else None
                spacefill_mapping["cardboard_box_gross_weight_in_kg"] = int(obj_cardbox.spacefill_cardboard_box_weight) if obj_cardbox.spacefill_cardboard_box_weight > 1 else None    
                spacefill_mapping["cardboard_box_net_weight_in_kg"] = int(obj_cardbox.spacefill_cardboard_box_weight) if obj_cardbox.spacefill_cardboard_box_weight > 1 else None

            
        return spacefill_mapping

    def get_values(self, vals):
        """ return the values to write, for the standard fields """
        for product in self:
            if product.weight:
                vals['each_gross_weight_in_kg'] = product.weight 
                vals['each_net_weight_in_kg'] = product.weight 

            if not product.default_code: 
                ref = product.name
                for attribute_value in self.product_template_attribute_value_ids:
                    tmpValue = attribute_value.name
                    ref += "" + attribute_value.attribute_id.name[0].upper() + tmpValue
                self.write({'default_code' : ref.replace(" " ,"")})
                vals['item_reference'] = ref.replace(" " ,"")
            else:
                vals['item_reference'] = product.default_code

            if product.item_spacefill_id:
                vals['item_reference'] = None

            return vals
        
    def get_spacefill_packing(self):
        """return the spacefill packaging values"""
        spacefill_pallet_qty = 0
        spacefill_cardboard_box_qty = 0
        if self.packaging_ids:
            for package in self.packaging_ids:
                if package.package_type_id.is_spacefill_cardboard_box:
                        spacefill_cardboard_box_qty = package.qty
                elif package.package_type_id.is_spacefill_pallet:
                        spacefill_pallet_qty = package.qty
        return spacefill_pallet_qty, spacefill_cardboard_box_qty
    
    def cron_update_inventory(self):
        """
            import product inventories from spacefill warehouse to odoo warehouse
        """
        products =self.search([('is_exported', '=', True ), ('item_spacefill_id', '!=', None)])
        for product in products:
            product.create_inventory_from_spacefill_with_lot()
    
    
    def create_inventory_from_spacefill_with_lot(self):
        """ Create inventory from spacefill warehouse with lot
        """
        # todo : check the difference between the actual odoo quantity and the stock in spacefill, if equal , don't write anything
        
        for company in self.env['res.company'].search([]):
            #company_env = self.env.with_context(force_company=company.id)
            setup = self.env['spacefill.config'].search([('company_id', '=',  company.id )], limit=1)
            if setup:
                instance = API(setup.spacefill_api_url,
                        setup.spacefill_shipper_token)
                whs= self.env['stock.warehouse'].search([('company_id','=',company.id),('is_exported','=',True)])
                if self.tracking !="none":
                    """ if lot or sn"""
                    """ get the lots from spacefill item"""
                    item_url = 'logistic_management/batches/'#+ self.item_spacefill_id +'/'
                    filter={'master_item_id':self.item_spacefill_id,'limit':10000} #to do : add pagination if more than n lines by item
                    vals= instance.search_read(instance.url+item_url,filter)# setup batches
                    lots =[]
                    for batch in vals:
                        item_url = 'logistic_management/batches/'+batch.get("id")+'/'
                        lot_line = instance.browse(instance.url+item_url)
                        lots.append(lot_line)
                    for lot in lots:
                        for wh in lot.get("stock_by_warehouse_by_batch"):
                            if wh.get("warehouse_id") in whs.mapped('spacefill_warehouse_account_id'):
                                warehouse = self.env['stock.warehouse'].search(
                                                [('company_id', '=', company.id),('spacefill_warehouse_account_id' ,'=',wh.get("warehouse_id"))], limit=1)
                                if warehouse:
                                    lot_odoo = self.env['stock.lot'].search([('name','=',lot.get("name")),('company_id', '=', company.id),('product_id','=', self.id)])
                                    if not lot_odoo:
                                        lot_odoo = self.env['stock.lot'].create({'name': lot.get("name"), 'product_id': self.id, 'company_id': company.id})
                                    inventory= self.env['stock.quant'].with_context(inventory_mode=True,from_spacefill=True).create({
                                        'product_id': self.id,
                                        'location_id': warehouse.lot_stock_id.id,
                                        'lot_id': lot_odoo.id,                                        
                                        'inventory_quantity': wh.get("number_of_each"),
                                       
                                    }).action_apply_inventory()
                                    self.message_post(body="Inventory updated from Spacefill")


                # vals = {"batch_name":batch_name, "each_qty":each_qty}
                else:
                    """ si pas de lot"""
                    item_url = 'logistic_management/master_items/'+ self.item_spacefill_id +'/'
                    vals= instance.browse(instance.url+item_url)

                    
                    for wh in vals.get("stock_by_warehouse"):
                            if wh.get("warehouse_id") in whs.mapped('spacefill_warehouse_account_id'):
                                warehouse = self.env['stock.warehouse'].search(
                                                [('company_id', '=', company.id),('spacefill_warehouse_account_id' ,'=',wh.get("warehouse_id"))], limit=1)
                                if warehouse:                                   

                                    inventory= self.env['stock.quant'].with_context(inventory_mode=True,from_spacefill=True).create({
                                                                                        'product_id': self.id,
                                                                                        'location_id': warehouse.lot_stock_id.id,
                                                                                        'inventory_quantity': wh.get("number_of_eaches"),                                                                             
                                                                                    }).action_apply_inventory()
                                    self.message_post(body="Inventory updated from Spacefill")
        return True
    #CRUDS 
    def write(self, vals):
        FIELDS_TO_TRIG =[ 'barcode', 'name', 'weight','packing_ids','packaging_ids','force_to_update']
        """
        if 'default_code' in vals:
            for product in self.filtered(lambda p: p.is_exported and p.item_spacefill_id):
                if product.default_code != vals['default_code']:
                    raise UserError(_("You can't change the reference of the product, if this product is exported in Spacefill"))     
        """
        res= super(ProductProduct, self).write(vals)
       
        for field in FIELDS_TO_TRIG:
            if field in vals : #'active' not in vals or  'item_spacefill_id' not in vals or 'is_exported' not in vals:
                for product in self.filtered(lambda p: p.is_exported and p.item_spacefill_id):                   
                    product.export_product_in_spacefill()       
        return res

    def _constrains_mandatory_fields(self):
        '''
            Check that the fields are sent correctly
        '''
        MANDATORY_FIELDS = ['detailed_type']
        for product in self:
            for field in MANDATORY_FIELDS:
                if field == 'detailed_type':
                    if product.detailed_type != 'product':
                        raise ValidationError(_('The detailed type must be product'))
                    else:
                        return True
    
    def unlink(self):
        #for product in self.filtered(lambda p: p.is_exported and p.item_spacefill_id):
        #    # unbale to archive the item by the API
        #    raise UserError(_("You can't delete the product, if this product is exported in Spacefill"))
        return super(ProductProduct, self).unlink()
 