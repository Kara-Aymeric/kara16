# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    def _get_default_agent_ids(self):
        return self.env['res.users'].search([]).ids

    used_default_agent = fields.Boolean(string="Used by default for agent")
    access_agent_ids = fields.Many2many('res.users', string="Agent access", default=_get_default_agent_ids)

    @api.model
    def create(self, vals):
        """ Surcharge create method """
        record = super(ProductPricelist, self).create(vals)
        for user in self.env['res.users'].search([]):
            user.sudo().action_update_access_products()

        return record

    def write(self, vals):
        """ Surcharge write method """
        res = super(ProductPricelist, self).write(vals)
        for user in self.env['res.users'].search([]):
            user.sudo().action_update_access_products()

        return res
