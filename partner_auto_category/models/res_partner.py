# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    use_as_default = fields.Boolean(string="Default Tags", copy=False)
    replace_after_invoice_category_id = fields.Many2one(
        "res.partner.category", string="Replace after invoicing by", copy=False
    )


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _default_category(self):
        """ Surcharge base function (base module) """
        res = super()._default_category()
        res |= self.env["res.partner.category"].search([("use_as_default", "=", True)])

        return res

    category_id = fields.Many2many(default=_default_category)
