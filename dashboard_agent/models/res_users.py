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

    restrict_custom_field = fields.Boolean(
        string="Restrict custom field", compute="_compute_restrict_custom_field"
    )
    restrict_custom_field_d2r = fields.Boolean(
        string="Restrict custom field D2R", compute="_compute_restrict_custom_field_d2r"
    )
    restrict_custom_field_ka = fields.Boolean(
        string="Restrict custom field KA", compute="_compute_restrict_custom_field_ka"
    )

    @api.depends('name')
    def _compute_restrict_custom_field(self):
        """ Compute readonly custom field """
        for record in self:
            restrict_custom_field = False
            user = self.env.user
            if user.has_group('dashboard_agent.group_external_agent') or user.has_group('dashboard_agent.group_principal_agent'):
                restrict_custom_field = True

            record.restrict_custom_field = restrict_custom_field

    @api.depends('name')
    def _compute_restrict_custom_field_d2r(self):
        """ Compute readonly custom field D2R """
        for record in self:
            restrict_custom_field_d2r = False
            user = self.env.user
            if user.has_group('dashboard_agent.group_external_agent'):
                restrict_custom_field_d2r = True

            record.restrict_custom_field_d2r = restrict_custom_field_d2r

    @api.depends('name')
    def _compute_restrict_custom_field_ka(self):
        """ Compute readonly custom field KA """
        for record in self:
            restrict_custom_field_ka = False
            user = self.env.user
            if user.has_group('dashboard_agent.group_principal_agent'):
                restrict_custom_field_ka = True

            record.restrict_custom_field_ka = restrict_custom_field_ka

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
