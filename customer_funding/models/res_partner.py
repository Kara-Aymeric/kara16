# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    credit_customer_ids = fields.One2many(
        'credit.customer',
        'partner_id',
        string="Credits customer"
    )

    def assign_customer_funding_auto(self):
        """ Assign customer funding auto """
        partner_financier_ids = self.env['partner.financier'].search([('add_auto_partner', '=', True)])
        for financier in partner_financier_ids:
            if financier.partner_id:
                self.env['credit.customer'].create({
                    'partner_id': self.id,
                    'partner_financier_id': financier.id,
                })

    @api.model
    def create(self, vals):
        """ Surcharge create method """
        record = super(ResPartner, self).create(vals)
        record.assign_customer_funding_auto()

        return record
