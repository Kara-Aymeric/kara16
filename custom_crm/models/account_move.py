# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    partner_typology_id = fields.Many2one(
        'partner.typology', string="Typology",
        store=True, compute="_compute_partner_typology_id"
    )

    partner_typology_id2 = fields.Many2one(
        'partner.typology', string="Specificity",
        store=True, compute="_compute_partner_typology_id2"
    )

    def _get_partner_typology(self, partner, typology_field):
        """
        Retrieves the typology from the parent or partner.
        :param partner: The partner concerned
        :param typology_field: The name of the typology field to retrieve
        :return: The ID of the typology found or False
        """
        if partner:
            if partner.parent_id:
                return getattr(partner.parent_id, typology_field).id if getattr(partner.parent_id, typology_field) \
                    else False
            return getattr(partner, typology_field).id if getattr(partner, typology_field) else False
        return False

    @api.depends('partner_id', 'partner_id.partner_typology_id', 'partner_id.parent_id.partner_typology_id')
    def _compute_partner_typology_id(self):
        """ Compute the partner typology """
        for account in self:
            partner_typology_id = False
            if account.partner_id:
                partner_typology_id = self._get_partner_typology(account.partner_id, 'partner_typology_id')

            account.partner_typology_id = partner_typology_id

    @api.depends('partner_id', 'partner_id.partner_typology_id2', 'partner_id.parent_id.partner_typology_id2')
    def _compute_partner_typology_id2(self):
        """ Compute the partner typology 2 """
        for account in self:
            partner_typology_id2 = False
            if account.partner_id:
                partner_typology_id2 = self._get_partner_typology(
                    account.partner_id, 'partner_typology_id2'
                )

            account.partner_typology_id2 = partner_typology_id2
