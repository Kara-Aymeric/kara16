# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    partner_typology_id = fields.Many2one(
        'partner.typology', string="Typology", required=True, domain=[('parent_id', '=', False)]
    )

    partner_typology_id2 = fields.Many2one(
        'partner.typology', string="Specificity", domain=[('parent_id', '!=', False)]
    )

    collaboration = fields.Selection(
        [('not_active', 'Not active'), ('active', 'Active')],
        default="not_active", tracking=True, string="Collaboration"
    )

    code_discount = fields.Char(string="Code discount")

    @api.onchange('partner_typology_id')
    def _onchange_partner_typology_id(self):
        if self.partner_typology_id:
            return {'domain': {'partner_typology_id2': [('parent_id', '=', self.partner_typology_id.id)]}}
        else:
            return {'domain': {'partner_typology_id2': [('parent_id', '!=', False)]}}

    # def _define_partner_ref(self):
    #     """ Define partner ref """
    #     partner_ref = ""
    #     for partner in self:
    #         partner_ref = f"{partner.id}"
    #         partner_ref = self.env['ir.sequence'].next_by_code('customer.reference') or _('New')
    #         partner_same_ref = self.env['res.partner'].search_count([('ref', '=', partner_ref)])
    #         if partner_same_ref:
    #             raise ValidationError(
    #                 _("There is already an identical reference. "
    #                   "Please change value sequence 'customer.reference' manually into settings "
    #                   "or contact your administrator.")
    #             )
    #
    #         return partner_ref
    #
    # @api.model_create_multi
    # def create(self, vals_list):
    #     """ Surcharge create method """
    #     partners = super(ResPartner, self).create(vals_list)
    #     for partner in partners:
    #         partner.ref = partner._define_partner_ref()
    #
    #     return partners
