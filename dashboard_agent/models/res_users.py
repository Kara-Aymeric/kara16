# -*- coding: utf-8 -*-
from odoo import api, models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    product_pricelist_ids = fields.Many2many(
        'product.pricelist',
        string="Allowed product pricelist",
        store=True,
        readonly=True
    )
    allowed_product_tmpl_ids = fields.Many2many(
        'product.template',
        string="Allowed product templates",
        store=True
    )
    allowed_product_ids = fields.Many2many(
        'product.product',
        string="Allowed products",
        store=True
    )

    def action_update_access_products(self):
        """ Force update pricelist """
        self.ensure_one()
        pricelist_ids = self.product_pricelist_ids
        product_tmpl_list = pricelist_ids.item_ids.product_tmpl_id.mapped('id')
        product_list = pricelist_ids.item_ids.product_id.mapped('id')
        self.write({
            'allowed_product_tmpl_ids': [(6, 0, product_tmpl_list)],
            'allowed_product_ids': [(6, 0, product_list)],
        })
        # Force apply rule
        rule_product_tmpl_id = self.env.ref("dashboard_agent.dashboard_rule_allowed_products_tmpl_user", False)
        rule_product_id = self.env.ref("dashboard_agent.dashboard_rule_allowed_products_user", False)
        if rule_product_tmpl_id:
            self.env['ir.rule'].browse(rule_product_tmpl_id.id).sudo().write({})
        if rule_product_id:
            self.env['ir.rule'].browse(rule_product_id.id).sudo().write({})
