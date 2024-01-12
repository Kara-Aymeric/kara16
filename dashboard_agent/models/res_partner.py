# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Set the default salesperson when a contact is created
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)

    godfather_id = fields.Many2one(
        'res.users', string="Godfather", compute="_compute_godfather_id", store=True, readonly=False, tracking=True
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

    @api.depends('user_id')
    def _compute_godfather_id(self):
        """ Get godfather """
        for order in self:
            godfather_id = order.godfather_id
            relation_agent_id = self.env['relation.agent'].sudo().search([
                ('godson_id', '=', order.user_id.id),
                ("start_date", "<=", fields.Date.today()),
                ("end_date", ">=", fields.Date.today())
            ], limit=1)
            if relation_agent_id:
                godfather_id = relation_agent_id.godfather_id

            order.godfather_id = godfather_id.id

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

    @api.model
    def _get_view(self, view_id=None, view_type='form', **options):
        arch, view = super()._get_view(view_id, view_type, **options)
        if self.env.user.has_group('dashboard_agent.group_external_agent'):
            if view_type == 'kanban':
                for node in arch.xpath("//kanban"):
                    node.set('create', 'false')
            if view_type == 'tree':
                for node in arch.xpath("//tree"):
                    node.set('create', 'false')
            if view_type == 'form':
                for node in arch.xpath("//form"):
                    node.set('create', 'false')
        return arch, view

    @api.model
    def create(self, vals):
        """ Surcharge create method """
        record = super(ResPartner, self).create(vals)
        user = self.env.user
        if user.has_group('dashboard_agent.group_external_agent') or user.has_group('dashboard_agent.group_principal_agent'):
            pricelist_id = self.env['product.pricelist'].search([('used_default_agent', '=', True)], limit=1)
            if pricelist_id:
                record['property_product_pricelist'] = pricelist_id.id

        return record
