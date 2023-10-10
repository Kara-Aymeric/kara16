# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _get_default_related_user_ids(self):
        """ Allows you to search only for contacts to agent """
        user_id = self.env.user
        users = []
        relation_agent_ids = self.env['relation.agent'].search([('agent_ids', 'in', user_id.id)])
        for relation_agent in relation_agent_ids:
            users.append(relation_agent.principal_agent_id.id)

        users.append(user_id.id)
        user_ids = self.env['res.users'].browse(users)

        return user_ids

    # Set the default salesperson when a contact is created
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user)

    # Provide multiple users access to each contact
    related_user_ids = fields.Many2many('res.users', string='Access Rights', default=_get_default_related_user_ids)
    readonly_custom_field = fields.Boolean(string="Readonly custom field", compute="_compute_readonly_custom_field")

    @api.depends('name')
    def _compute_readonly_custom_field(self):
        """ Compute readonly custom field """
        for record in self:
            readonly_custom_field = False
            user = self.env.user
            if user.has_group('dashboard_agent.group_external_agent') or user.has_group('dashboard_agent.group_principal_agent'):
                readonly_custom_field = True

            record.readonly_custom_field = readonly_custom_field

    # Automatically sync salesperson and related users from parent to child
    @api.model
    def _commercial_fields(self):
        return super(ResPartner, self)._commercial_fields() + \
               ['user_id', 'related_user_ids']

    @api.model
    def create(self, vals):
        """ Surcharge create method """
        record = super(ResPartner, self).create(vals)
        user = self.env.user
        if user.has_group('dashboard_agent.group_external_agent') or user.has_group('dashboard_agent.group_principal_agent'):
            record['property_product_pricelist'] = self.env['product.pricelist'].search(
                [('used_default_agent', '=', True)], limit=1
            )

        return record
