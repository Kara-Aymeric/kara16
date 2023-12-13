# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Set the default salesperson when a contact is created
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)
    godfather_id = fields.Many2one(
        'res.users', string="Godfather", compute="_compute_godfather_id", store=True, readonly=False, tracking=True
    )

    # Provide multiple users access to each contact
    restrict_custom_field = fields.Boolean(string="Restrict custom field", compute="_compute_restrict_custom_field")
    readonly_custom_field = fields.Boolean(string="Readonly custom field")  # TO DELETED

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
