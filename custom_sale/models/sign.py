# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class SignTemplate(models.Model):
    _inherit = "sign.template"

    order_id = fields.Many2one(comodel_name='sale.order', string="Order")


class SignRequest(models.Model):
    _inherit = "sign.request"

    order_id = fields.Many2one(comodel_name='sale.order', string="Order")

    def _get_order_sign_template(self):
        """ Get the command linked to the signature model """
        for record in self:
            if record.template_id:
                if record.template_id.order_id:
                    return record.template_id.order_id
            return False

    @api.model
    def create(self, vals):
        """ Surcharge create method """
        record = super(SignRequest, self).create(vals)
        order_id = record._get_order_sign_template()
        if order_id:
            record['order_id'] = order_id.id

        return record

    def write(self, vals):
        """ Surcharge write method """
        for record in self:
            if vals.get('state', False) == 'signed':
                if record.order_id:
                    record.order_id.with_context(external_update=True).write({'sign_request_id': record.id})
                    record.order_id.with_context(external_update=True).action_confirm_supplier()
            if vals.get('completed_document', False) and record.order_id:
                record.order_id.with_context(external_update=True).write(
                    {
                        'e_supplier_quote_signed': vals.get('completed_document', False),
                        'e_supplier_quote_filename_signed': f"Signed_{record.order_id.e_supplier_quote_filename or 'quote'}"
                    }
                )

        return super(SignRequest, self).write(vals)


class SignItemType(models.Model):
    _inherit = "sign.item.type"

    active = fields.Boolean(default=True, tracking=True,
                            help="By unchecking the active field, you can hide a item type without deleting it.")
