# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    access_commission = fields.Boolean(string="Access commission", related="company_id.access_commission")
    commission_type = fields.Selection(
        [('percentage', 'Percentage'), ('fixed', 'Fixed')], string="Commission type", tracking=True)
    percentage_value = fields.Float(string="Percentage value",
                                    help="Value to calculate the commission on the product", tracking=True)
    sale_commission = fields.Float(string="Commission", store=True, compute="_compute_commission", digits=(12, 2),
                                   help="Final value of the commission calculated automatically if the type of "
                                        "commission is 'percentage'", tracking=True)
    agent_commission_ids = fields.One2many('agent.commission', 'product_template_id', string="Agent commission")

    @api.depends('commission_type', 'percentage_value', 'list_price')  # VOIR POUR UN ONCHANGE
    def _compute_commission(self):
        for product in self:
            if product.commission_type == 'percentage' and product.percentage_value > 0:
                product.sale_commission = (product.percentage_value/100) * product.list_price

    @api.onchange('commission_type')
    def _onchange_commission_type(self):
        if self.commission_type == 'fixed':
            self.percentage_value = 0

    @api.onchange('percentage_value')
    def _onchange_percentage_value(self):
        if self.percentage_value < 0:
            raise ValidationError("The percentage value cannot be negative")

    @api.onchange('sale_commission')
    def _onchange_sale_commission(self):
        if self.sale_commission < 0:
            raise ValidationError("The amount of a commission cannot be negative")
        if self.list_price < self.sale_commission:
            raise ValidationError("The selling price cannot be lower than the commission on the product")
