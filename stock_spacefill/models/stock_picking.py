#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright: (c) 2022 irokoo
:license: AGPLv3, see LICENSE for more details

"""
from odoo import api, fields, models, _
from odoo.addons.stock_spacefill.spacefillpy.api import API as API
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import logging
import html
_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    order_spacefill_id = fields.Char('SpaceFill order ID',copy=False)
    status_spacefill = fields.Char('Last order status',copy=False)
    only_manage_by_spacefill = fields.Boolean('Only manage by Spacefill', related='picking_type_id.only_manage_by_spacefill', store=True) 
    label_spacefill = fields.Char('Label Spacefill',compute='_compute_label_spacefill')

    @api.model
    def _compute_label_spacefill(self):
        for picking in self:
            if picking.only_manage_by_spacefill:
                if picking.order_spacefill_id:
                    if picking.status_spacefill =='WAREHOUSE_NEEDS_TO_CONFIRM_PLANNED_EXECUTION_DATE_STATE' or \
                                                    picking.status_spacefill =='SHIPPER_NEEDS_TO_SUGGEST_NEW_PLANNED_EXECUTION_DATE_STATE' or \
                                                    picking.status_spacefill =='ORDER_IS_READY_TO_BE_EXECUTED_STATE' or \
                                                    picking.status_spacefill =='DRAFT_ORDER_STATE':                                      
                        picking.label_spacefill = "IN_PROGRESS"
                    elif picking.status_spacefill =='UNLOADING_STARTED_STATE':
                        picking.label_spacefill = "UNLOADING_STARTED"
                    elif picking.status_spacefill =='UNLOADING_FINISHED_STATE':
                        picking.label_spacefill = "UNLOADING_FINISHED"
                    elif picking.status_spacefill =='PREPARATION_STARTED_STATE':
                        picking.label_spacefill = "PREPARATION_STARTED"
                    elif picking.status_spacefill =='PREPARATION_FINISHED_STATE':
                        picking.label_spacefill = "PREPARATION_FINISHED"
                    elif picking.status_spacefill =='CANCELED_ORDER_STATE' or \
                                                picking.status_spacefill =='FAILED_ORDER_STATE':
                        picking.label_spacefill = "CANCELED"
                    elif picking.status_spacefill =='COMPLETED_ORDER_STATE':
                        picking.label_spacefill = "COMPLETED"
                else:
                    picking.label_spacefill = "WAITING_AVAILABILITY"
            else:
                picking.label_spacefill = "NONE"

    # METHODS    
    def get_instance_spacefill(self):
        """Get instance of Spacefill API."""
        setup = self.env['spacefill.config'].search([('company_id', '=',self.company_id.id)], limit=1)
        if not setup:
            raise UserError(_('Please configure Spacefill first.'))
        instance = API(setup.spacefill_api_url,
                       setup.spacefill_shipper_token)        
        return instance,setup
    
    @api.model  
    def cron_maj_status(self):
        """This method is called by the cron 'update status Spacefill'."""
        _logger.info('Start cron update status Spacefill')
        res= self.env['spacefill.update'].check_availability()

        pickings = self.env['stock.picking'].search([
                            ('order_spacefill_id', '!=', False),
                            ('state','not in',['done']),                           
                         
                ])
        for picking in pickings:
            if picking.only_manage_by_spacefill:
                picking.update_status_spacefill_with_lot()
        _logger.info('End cron update status Spacefill')
           
    def action_server_synchronize_order(self):
        """ This method is called by the button 'update Spacill' in the form view of the picking."""
        for picking in self:
                if picking.picking_type_id.warehouse_id.is_exported and picking.state not in ['done','cancel']:
                        if picking.picking_type_code == 'incoming':            
                            picking.export_order_entry_to_spacefill()

                        elif picking.picking_type_code == 'outgoing':                                     
                            picking.export_order_exit_to_spacefill()
                                            
                        elif picking.picking_type_code == 'internal':
                                             picking.message_post(
                                            body=_('Internal transfert is not allowed for Spacefill warehouse') 
                                            )
         
                           
    def check_spacefill_status(self):
        """Check if status is ok to update"""
        url = "logistic_management/orders/"
        if self.order_spacefill_id:            
            spacefill_instance, setup = self.get_instance_spacefill()
            data = spacefill_instance.browse(setup.spacefill_api_url + url + str(self.order_spacefill_id) + '/')
            spacefill_statut = self.env['spacefill.statut'].search([('spacefill_statut', '=', data.get('status'))])
            if spacefill_statut:
                if spacefill_statut.is_ok_to_update:
                    return True
                else:
                    self.message_post(
                                    body=_('Update is not allowed at this step')
                                    )
                    res=  self.env['spacefill.update'].search([('id_to_update','=',self.id),('is_to_update','=',True)])
                    if res:
                        res.is_to_update=False    


   
    
    def update_status_spacefill_with_lot(self):
        """Update status of order in spacefill with lot"""
        url = "logistic_management/orders/"
        filter={}
        setup = self.env['spacefill.config'].search([('company_id', '=',self.company_id.id)], limit=1)
        spacefill_instance = API(setup.spacefill_api_url,
                       setup.spacefill_shipper_token)    
        data = spacefill_instance.browse(setup.spacefill_api_url + url + str(self.order_spacefill_id) + '/')
        if data and self.order_spacefill_id:
            spacefill_statut = self.env['spacefill.statut'].search([('spacefill_statut', '=', data.get('status'))])
        else:
            spacefill_statut = False
        if spacefill_statut:            
            self = self.with_context(
                _send_on_write="NO")
            if self.status_spacefill != spacefill_statut.spacefill_statut:
                self.write({'status_spacefill': spacefill_statut.spacefill_statut})
                self.message_post(body="Update SpaceFill Status : %s" % spacefill_statut.spacefill_statut)
            if spacefill_statut.is_default_done and (self.state != 'done' or self.state !='cancel'):
                for line in data.get('order_items'):
                    product = self.env['product.product'].search([('item_spacefill_id', '=', line.get('master_item_id'))], limit=1)                    
                    line_id = False
                    if product:
                        if line.get('batch_name'):
                            lot = self.env['stock.production.lot'].search([('name', '=', line.get('batch_name')),('product_id','=',product.id),('company_id','=',self.company_id.id)], limit=1)
                            if not lot:
                                lot = self.env['stock.production.lot'].create({
                                                                                            'name': line['batch_name'],
                                                                                            'company_id': self.company_id.id,
                                                                                            'product_id': product.id
                                                                                        })                               
                            
                            line_id = self.env['stock.move.line'].search([('picking_id','=',int(data.get('edi_erp_id'))),('product_id','=',product.id),('lot_id','=',lot.id)])
                            if not line_id:
                                    self.create_new_line(line, product,lot)
                            else:
                                    line_id.write({'qty_done': int(line.get('actual_quantity'))})
                                    line_id.write({'lot_id': lot.id})
                           

                        else:
                            line_id = self.env['stock.move.line'].search([('picking_id','=',int(data.get('edi_erp_id'))),('product_id','=',product.id)])
                            line_id.write({'qty_done': int(line.get('actual_quantity'))})
                        # add unknow item
                    else:
                        self.message_post(body="Item %s is not found in Odoo" % line.get('master_item_id'))  

                self.with_context(skip_backorder=True, picking_ids_not_to_backorder=self.ids,from_spacefill=True).button_validate()
                """ 'effective_executed_at': '2022-10-26T11:00:00+00:00'"""
                date_effective = data.get('effective_executed_at')
                if date_effective:
                    date_effective = datetime.strptime(date_effective[:19].replace('T',' '), '%Y-%m-%d %H:%M:%S')
                    self.write({'date_done': date_effective})
                comment = data.get('comment')
                if comment:
                    self.message_post(body=_("Spacefill operation comment: %s" % comment))

            if spacefill_statut.is_default_cancel:
               # to do : chekc if picking is canceled too

               return True
        return True

    def create_new_line(self, line, product,lot):
        """
        Create a new line in the picking
        """
        StockMoveLine = self.env['stock.move.line']
        move_line_id = StockMoveLine.create({
            'picking_id': self.id,
            'product_id': product.id,
            'qty_done': line.get('actual_quantity', 0),
            'lot_id': lot.id,
            'location_id': self.location_id.id,
            'location_dest_id': self.location_dest_id.id,
            'product_uom_id': product.uom_id.id,
        })
        return move_line_id


    
    def export_order_entry_to_spacefill(self):
        """Export entry order to spacefill"""
        instance, setup = self.get_instance_spacefill()
        self.create_or_update_spacefill(instance, setup,'ENTRY')

        return True
    def export_order_exit_to_spacefill(self):
        """Export exit order to spacefill"""
        instance, setup = self.get_instance_spacefill()
        self.create_or_update_spacefill(instance, setup,'EXIT')
        return True
    
    def create_or_update_spacefill(self, instance, setup,type):
        """Create or update order in spacefill"""
        order_items = []

        """Check the scheduled date and the deadline date respect the delay"""
        delay = setup.spacefill_delay+1 or 25 # 24 hours + 1 hour
        date_delay = fields.Datetime.from_string(fields.Datetime.now())\
                   + relativedelta(hours=delay)
        if self.scheduled_date < date_delay:
            scheduled_date = date_delay
            self.message_post(body=_("The scheduled date is before the delay of %s hours, the scheduled date is transmitted to %s" % (setup.spacefill_delay, scheduled_date)))
        else:
            scheduled_date = self.scheduled_date

        if self.date_deadline  < self.scheduled_date:
            raise UserError(_('The deadline date must be after the scheduled date'))
        if self.date_deadline  < date_delay:
            deadline_date= date_delay
            self.message_post(body=_("The deadline date is before the delay of %s hours, the deadline date is trasnmitted to %s" % (setup.spacefill_delay, deadline_date)))
        else:
            deadline_date = self.date_deadline
        
        if type =='ENTRY':
            order_values = self.prepare_entry_vals(scheduled_date,deadline_date)
            item_url = 'logistic_management/orders/entry/'
        else:
            order_values = self.prepare_exit_vals(scheduled_date,deadline_date)
            item_url = 'logistic_management/orders/exit/'

        vals= self.sanitize_lines(self.move_line_ids)
        for line in vals:
            for lot in vals[line]:
                      
                order_lines_values = {}       
                order_lines_values['master_item_id'] = vals[line][lot]['master_item_id']
                # self.get_item_packaging_type(item)
                order_lines_values["item_packaging_type"] = "EACH"
                order_lines_values["expected_quantity"] = vals[line][lot]['qty']
                order_lines_values['batch_name'] = lot if lot else None
                order_items.append(
                    order_lines_values
                    )
        order_values.update({"order_items": order_items})
        if self.order_spacefill_id and self.check_spacefill_status():
            self = self.with_context(
                _send_on_write="NO") 
            item_url ='logistic_management/orders/'+self.order_spacefill_id+'/shipper_updates_order_action'
            res = instance.call('POST',instance.url+item_url, order_values)
            if isinstance(res, dict):
                self.message_post(
                                    body=_('Order %s is updated to Spacefill' ) % self.order_spacefill_id
                                    )
            else:
                raise UserError(
                        _('Error from API : %s') % res)
            
        else:
            if not self.order_spacefill_id:                        
                res = instance.create(instance.url+item_url, order_values)
                self = self.with_context(
                _send_on_write="NO")    
                if isinstance(res,dict):
                    self.write({'order_spacefill_id': res.get('id')})
                    self.write({'status_spacefill': res.get('status')})
                    self.message_post(
                                        body=_('Order is created to Spacefill ID :%s') % self.order_spacefill_id
                                        )
                else:
                    raise UserError(
                            _('Error from API :%s') % res)
        
    def sanitize_lines(self,lines):
        """Sanitize lines to have only one line by item and lot"""
        qty_by_item_lot={}
        for line in lines:
            if line.product_uom_qty != 0 and line.product_id.item_spacefill_id: 
                if line.product_id.id not in qty_by_item_lot:
                    qty_by_item_lot[line.product_id.id] = {line.lot_name: {'product_id':line.product_id.id,'qty':0,'master_item_id':line.product_id.item_spacefill_id}}
                if line.lot_name not in qty_by_item_lot[line.product_id.id].keys():
                    qty_by_item_lot[line.product_id.id][line.lot_name] = {'product_id':line.product_id.id,'qty':0,'master_item_id':line.product_id.item_spacefill_id}
                qty_by_item_lot[line.product_id.id][line.lot_name]['qty'] += line.product_uom_qty
            else:
                self.message_post( body=_('Product %s is not exported or qty is 0 ,  please export it or add qty  and update this order' ) % line.product_id.name)
                # to add : auto-export ?
        return qty_by_item_lot                                                
                


    def prepare_entry_vals(self,scheduled_date,deadline_date):
        """Prepare the values for the entry order to send to Spacefill."""
        vals = {
            "shipper_order_reference": self.name,
            "warehouse_id": self.picking_type_id.warehouse_id.spacefill_warehouse_account_id,
            "comment": html.unescape(self.note) if self.note else None,
            "planned_execution_datetime_range": {
                "datetime_from": str(scheduled_date),
                "datetime_to": str(deadline_date)
            },
            "carrier_name": self.carrier_id.name if self.carrier_id else None,
            "carrier_phone_number": None,
            "transport_management_owner": "PROVIDER",
            "entry_expeditor": self.partner_id.name,
            "entry_expeditor_address_line1":self.partner_id.street,
            "entry_expeditor_address_zip": self.partner_id.zip,
            "entry_expeditor_address_details": self.partner_id.street2 if self.partner_id.street2 else None,
            "entry_expeditor_address_city": self.partner_id.city,
            "entry_expeditor_address_country": self.partner_id.country_id.name,
            "entry_expeditor_address_lat": None,
            "entry_expeditor_address_lng": None,
            "entry_expeditor_planned_datetime_range": {
                "datetime_from": str(scheduled_date),
                "datetime_to": str(deadline_date)
            },
            "edi_erp_id": self.id,
            "edi_wms_id": None,
            "edi_tms_id": None,
            "transfered_to_erp_at": datetime.utcnow().isoformat() + "Z",
            "transfered_to_wms_at": None,
            "transfered_to_tms_at": None,

        }
        return vals
    def prepare_exit_vals(self,scheduled_date,deadline_date):
        """Prepare the values of the order to export on Spacefill.
        
        :param scheduled_date: Scheduled date of the order"""
        
        vals= {
            "shipper_order_reference": self.name,
            "warehouse_id": self.picking_type_id.warehouse_id.spacefill_warehouse_account_id,#
            "comment": html.unescape(self.note) if self.note else None,
            "planned_execution_datetime_range": {
                "datetime_from": str(scheduled_date),
                "datetime_to": str(deadline_date),
            },
            "carrier_name": self.carrier_id.name if self.carrier_id else None,
            "carrier_phone_number": None,
            "transport_management_owner": "PROVIDER",
            "exit_final_recipient":self.partner_id.name,
            "exit_final_recipient_address_line1": self.partner_id.street,
            "exit_final_recipient_address_zip": self.partner_id.zip,
            "exit_final_recipient_address_details": self.partner_id.street2 if self.partner_id.street2 else None,
            "exit_final_recipient_address_city": self.partner_id.city,
            "exit_final_recipient_address_country": self.partner_id.country_id.name,
            "exit_final_recipient_address_lat": None,
            "exit_final_recipient_address_lng": None,
            "exit_final_recipient_planned_datetime_range": {
                "datetime_from": str(scheduled_date),
                "datetime_to": str(deadline_date),
            },
            "edi_erp_id": self.id,
            "edi_wms_id": None,
            "edi_tms_id": None,
            "transfered_to_erp_at": datetime.utcnow().isoformat() + "Z",
            "transfered_to_wms_at": None,
            "transfered_to_tms_at": None,                        
        }        

        return vals
    

    # CRUD / STD METHODS
    """
    def create(self, vals):
        res=super(StockPicking, self).create(vals)
        for picking in self:
             if picking.picking_type_id.warehouse_id.is_exported: # and self.env.context.get('_send_on_write')!='NO' and res.state not in ['done','cancel']:
                 if not self.env['spacefill.update'].search([('id_to_update','=',res.id),('is_to_update','=',True)]):
                    self.env['spacefill.update'].create({'id_to_update':res.id,'is_to_update':True})                
        return res
    """
    
    def write(self,vals): 
        res=super(StockPicking, self).write(vals)
        for picking in self:
            if picking.picking_type_id.warehouse_id.is_exported and self.env.context.get('_send_on_write')!='NO' and picking.state not in ['done','cancel']:
                if not self.env['spacefill.update'].search([('id_to_update','=',picking.id),('is_to_update','=',True)]):
                    self.env['spacefill.update'].create({'id_to_update':picking.id,'is_to_update':True,'triggered_from':'write_picking'})
        return res

 
    def do_unreserve(self):
        res= super(StockPicking, self).do_unreserve()
        for picking in self:
            if picking.picking_type_id.warehouse_id.is_exported:
                if picking.check_spacefill_status():
                    self.env['spacefill.update'].create({'id_to_update':picking.id,'is_to_update':True,'triggered_from':'unreserve_picking'})
        return res
    def action_assign(self):
        res= super(StockPicking, self).action_assign()
        for picking in self:
            if picking.picking_type_id.warehouse_id.is_exported:
                if picking.check_spacefill_status():
                    self.env['spacefill.update'].create({'id_to_update':picking.id,'is_to_update':True,'triggered_from':'assign_picking'})
        return res
    
    def button_validate(self):
        if self.only_manage_by_spacefill and not self.env.context.get('from_spacefill')==True:
            self.message_post(body="This picking is managed by Spacefill, you can't validate it")
        else:
            return super(StockPicking, self).button_validate()
    
    def action_cancel(self):
        res = super(StockPicking, self).action_cancel()
        for picking in self:
            if picking.picking_type_id.warehouse_id.is_exported:
                if picking.check_spacefill_status():
                    picking.export_order_cancel_to_spacefill()
                    picking.update_status_spacefill_with_lot()
        return res

    def unlink(self):
        for picking in self:
            if picking.picking_type_id.warehouse_id.is_exported:
                if picking.check_spacefill_status():
                    picking.export_order_cancel_to_spacefill() 
                    picking.update_status_spacefill_with_lot()
        return super(StockPicking, self).unlink()


    def copy(self, default=None):
        for picking in self:
            if picking.only_manage_by_spacefill:
                    raise UserError(_('You can not duplicate a picking managed by Spacefill'))
            else:
                    return super(StockPicking, self).copy(default)

    def export_order_cancel_to_spacefill(self):
        url = "logistic_management/orders" #/{order_id}/shipper_cancels_order_action/"        
        spacefill_instance, setup = self.get_instance_spacefill()
        res = spacefill_instance.call('POST',setup.spacefill_api_url + url +'/'+ str(self.order_spacefill_id) + '/shipper_cancels_order_action',None)
        if isinstance(res, dict):
                    self.message_post(
                                    body=_('Order %s is Canceled to Spacefill' ) % self.order_spacefill_id
                                    )
        else:
                raise UserError(
                        _('Error from SpaceFill API : %s') % res)
   
    
    def action_put_in_pack(self):
        if self.only_manage_by_spacefill:
            raise UserError(_('You can not validate a picking managed by Spacefill'))
        else:
            return super(StockPicking, self).action_put_in_pack()

 
    