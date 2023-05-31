# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AgentCommission(models.Model):
    _name = 'agent.commission'
    _description = 'Agent commission'

    user_id = fields.Many2one('res.users', string="Agent")
    percentage_value = fields.Float(string="Percentage value",
                                    help="Value to calculate the commission on the product", tracking=True)
    sale_commission = fields.Float(string="Commission", store=True, compute="_compute_sale_commission", digits=(12, 2),
                                   help="Final value of the commission calculated automatically", tracking=True)
    product_template_id = fields.Many2one('product.template', string="Product")

    @api.depends('percentage_value', 'product_template_id.list_price')
    def _compute_sale_commission(self):
        for record in self:
            if record.percentage_value > 0:
                record.sale_commission = (record.percentage_value/100) * record.product_template_id.list_price

    @api.onchange('percentage_value')
    def _onchange_percentage_value(self):
        if not 0 <= self.percentage_value <= 100:
            raise ValidationError("The percentage value must be between 0 and 100")
