# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def _get_supplier_id_domain(self):
        """ Allows you to search only for contacts with the supplier label """
        domain = []
        if self.env.company.trading_business:
            domain = [('category_id.id', '=', self.env.ref('custom_sale.kara_res_partner_category_supplier', False))]
        return domain

    @api.model
    def _get_partner_id_domain(self):
        """ Allows you to search only for contacts with the supplier label """
        domain = []
        if self.env.company.trading_business:
            domain = [('category_id.id', '=', self.env.ref('custom_sale.kara_res_partner_category_supplier', False))]
        return domain

    @api.model
    def _get_customer_id_domain(self):
        """ Allows you to search only for contacts with the customer label """
        return [('category_id.id', '=', self.env.ref('custom_sale.kara_res_partner_category_customer', False))]

    trading_business = fields.Boolean(string="Trading business", related="company_id.trading_business")
    partner_id = fields.Many2one(domain=_get_partner_id_domain)
    supplier_id = fields.Many2one(
        'res.partner',
        string="Supplier", help="Industrial or warehouse", domain=_get_supplier_id_domain, tracking=True,
        compute="_compute_supplier_id", store=True, readonly=False
    )
    customer_id = fields.Many2one('res.partner', string="Final customer", domain=_get_customer_id_domain, tracking=True)

    @api.depends('partner_id')
    def _compute_supplier_id(self):
        """ Supplier equal partner """
        for lead in self:
            supplier_id = False
            if lead.trading_business:
                supplier_id = lead.partner_id
            lead.supplier_id = supplier_id

    @api.onchange('supplier_id')
    def _onchange_supplier_id(self):
        """ Supplier equal partner """
        if self.trading_business:
            self.partner_id = self.supplier_id.id

    @api.onchange('partner_id')
    def _onchange_kara_partner_id(self):
        """ Partner equal supplier """
        if self.trading_business:
            self.supplier_id = self.partner_id.id
        if not self.partner_id.email or not self.partner_id.phone or not self.partner_id.mobile:
            self._force_clean_fields()

    def _force_clean_fields(self):
        """
        Force same fields to delete the value if the expected value is not filled in on the selected contact's card
        """
        if not self.partner_id.email:
            self.email_from = False
        if not self.partner_id.phone:
            self.phone = False
        if not self.partner_id.mobile:
            self.mobile = False

    def _prepare_opportunity_quotation_context(self):
        """ Surcharge method for add default customer when to create new quote """
        res = super(CrmLead, self)._prepare_opportunity_quotation_context()
        if self.trading_business:
            res.update({
                'default_customer_id': self.customer_id.id,
            })

        return res
