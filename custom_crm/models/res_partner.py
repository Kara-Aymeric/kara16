# -*- coding: utf-8 -*-
from odoo import api, fields, models


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
        string="Collaboration", compute='_compute_collaboration', store=True,
    )
    listprice_update_date = fields.Date(string="Listprice update date", compute='_compute_listprice_update_date')
    code_discount = fields.Char(string="Code discount")
    ref = fields.Char(tracking=True)

    @api.depends('invoice_ids.state', 'parent_id.invoice_ids.state', 'child_ids.invoice_ids.state')
    def _compute_collaboration(self):
        """ Collaboration is active if partner, parent, or children have posted invoices """
        for partner in self:
            all_invoices = partner.invoice_ids | partner.parent_id.invoice_ids | partner.child_ids.invoice_ids
            has_posted_invoice = any(inv.state == 'posted' for inv in all_invoices)
            partner.collaboration = 'active' if has_posted_invoice else 'not_active'

    @api.depends('property_product_pricelist', 'property_product_pricelist.write_date')
    def _compute_listprice_update_date(self):
        """ Compute date update pricelist """
        for partner in self:
            listprice_update_date = False
            if partner.property_product_pricelist:
                listprice_update_date = partner.property_product_pricelist.write_date

            partner.listprice_update_date = listprice_update_date

    @api.onchange('partner_typology_id')
    def _onchange_partner_typology_id(self):
        if self.partner_typology_id:
            self.partner_typology_id2 = False
            return {'domain': {'partner_typology_id2': [('parent_id', '=', self.partner_typology_id.id)]}}
        else:
            return {'domain': {'partner_typology_id2': [('parent_id', '!=', False)]}}

    def _define_partner_ref(self):
        """ Define partner ref """
        for partner in self:
            initial_partner = partner.name[:2].upper()
            typo_code = (
                partner.partner_typology_id2.code
                if partner.partner_typology_id2
                else partner.partner_typology_id.code
            )
            # Format the partner ID with leading zeros to ensure 6 digits
            formatted_id = str(partner.id).zfill(6)
            partner_ref = f"{initial_partner}{typo_code}{formatted_id}"

            return partner_ref

    @api.model_create_multi
    def create(self, vals_list):
        """ Surcharge create method """
        partners = super(ResPartner, self).create(vals_list)
        for partner in partners:
            partner.ref = partner._define_partner_ref()

        return partners

    def write(self, vals):
        """ Surcharge write method """
        res = super(ResPartner, self).write(vals)
        if "name" in vals or "partner_typology_id" in vals or "partner_typology_id2" in vals:
            for partner in self:
                partner.ref = partner._define_partner_ref()

        return res
