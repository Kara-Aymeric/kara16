#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""


:copyright: (c) 2022 irokoo
:license: AGPLv3, see LICENSE for more details


"""
from odoo import api, fields, models, _
from odoo.addons.stock_spacefill.spacefillpy.api import API as API
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
import html

class SpacefillConfig(models.Model):
    """Spacefill Config"""

    _name = "spacefill.config"
    _description = "spacefill.config"

    #spacefill_lsp_token = fields.Char(string='Token LSP')
    spacefill_shipper_token = fields.Char(string='Shipper company access Token')
    spacefill_api_url = fields.Char(string='API base url')
    spacefill_erp_account_id =fields.Char(string='SpaceFill Shipper company ID')
    spacefill_delay = fields.Integer("Notice period (in hours)")
    spacefill_confirm_schedule = fields.Boolean("Warehouse needs to confirm scheduling",default=False)
    

    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company,
        index=True, readonly=True, required=True,
        help='The company is automatically set from your user preferences.')
    spacefill_wh_count = fields.Integer(compute='_compute_spacefill_wh_count', string='Spacefill Warehouse',default=0)
    spacefill_products_count = fields.Integer(compute='_compute_spacefill_products_count', string='Spacefill Products',default=0)
    spacefill_stock_packaging_type_count = fields.Integer(compute='_compute_spacefill_stock_packaging_type_count', string='Spacefill Stock Packaging Type',default=0)


    @api.model
    def create(self,vals):
        if 'company_id' in vals :
            if vals['company_id'] == self.env.company.id:
                 raise UserError(_('You cannot create a spacefill setup for the same company as your user.'))
        if self.search([('company_id', '=', self.env.company.id)]):
            raise UserError(_('You cannot create a spacefill setup for the same company as your user.'))
        res = super(SpacefillConfig, self).create(vals)
        return res

    @api.model
    def default_get(self, fields):
        
        res = super(SpacefillConfig, self).default_get(fields)
        if not self.search([('company_id', '=', self.env.company.id)]):
            #raise UserWarning(_('You cannot create a spacefill config for the same company as your user.'))
            res['spacefill_api_url'] = 'https://api.spacefill.fr/v1/'
            res['spacefill_delay'] = 24
            res['spacefill_confirm_schedule'] = True

        return res


    def write(self, vals):
        if 'company_id' in vals:
            raise UserError(_('You cannot change the company of a spacefill setup.'))
        res = super(SpacefillConfig, self).write(vals)
        return res  

    def create_spacefill_info_request(self):        
        company = self.env.company.name if self.env.company.name else "NC"
        contact_name= self.env.user.name if self.env.user.name else "NC"
        contact_email = self.env.user.email if self.env.user.email else "NC"
        contact_phone = self.env.user.phone if self.env.user.phone else "NC"  
        contact_message = "<p>Please contact me to discuss about the integration of my company in SPACEFILL</p><br>"
        body = _("<p>Message"+contact_message+"</p><br>"+"<p>Company: "+company+"<br>"+"Contact name: "+contact_name+"<br>"+"Contact email: "+contact_email+"<br>"+"Contact phone: "+contact_phone+"<br>"+"<p>Unsubscribe: <a href='mailto:dpo@spacefill.fr'>unsubscribe</a></p>")
        #push better marketing way to Spacefill
        #send mail to Spacefill
        vals = {
                    'subject': 'SPACEFILL - Odoo integration request',
                    'body_html': body,
                    'email_to': 'sales@spacefill.fr',
                    'email_cc': contact_email,
                    'auto_delete': False,
                    'email_from': contact_email ,
                }

        mail_id = self.env['mail.mail'].sudo().create(vals)
        mail_id.sudo().send()
        return True
    def _compute_spacefill_wh_count(self):
        for config in self:
            config.spacefill_wh_count = self.env['stock.warehouse'].search_count([('is_exported', '=', True),('company_id','=',config.company_id.id)])
    
    def action_list_wh(self):
        return {
            'name': _('Warehouses'),
            'view_mode': 'tree,form',
            'res_model': 'stock.warehouse',
            'type': 'ir.actions.act_window',
            'domain': [('is_exported', '=', True),('company_id','=',self.company_id.id)],
        }
    def _compute_spacefill_products_count(self):
        for config in self:
            config.spacefill_products_count = self.env['product.product'].search_count([('is_exported', '=', True)])
    
    def action_list_products(self):
        return {
            'name': _('Products'),
            'view_mode': 'tree,form',
            'res_model': 'product.product',
            'type': 'ir.actions.act_window',
            'domain': [('is_exported', '=', True)],
        }
    
    def _compute_spacefill_stock_packaging_type_count(self):
        for config in self:
            config.spacefill_stock_packaging_type_count = self.env['stock.package.type'].search_count([('is_spacefill_pallet', '=', True)]) + self.env['stock.package.type'].search_count([('is_spacefill_cardboard_box', '=', True)])
    
    def action_list_stock_packaging_type(self):
        return {
            'name': _('Stock Packaging Type'),
            'view_mode': 'tree,form',
            'res_model': 'stock.package.type',
            'type': 'ir.actions.act_window',
            'domain': ['|',('is_spacefill_pallet', '=', True),('is_spacefill_cardboard_box', '=', True)],
        }