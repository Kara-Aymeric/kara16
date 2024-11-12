# -*- coding: utf-8 -*-
from odoo import models, fields, api


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
