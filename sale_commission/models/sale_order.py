# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    access_commission = fields.Boolean(string="Active commission option on the company",
                                       related="company_id.access_commission")
    commission_order = fields.Boolean(string="Commission")
    child_id = fields.Many2one('sale.order', string="Associated commission",
                               help="This sale allows to make the connection of the main sale "
                                    "for sale (commission) which will be invoiced to the industrial")
    order_origin_id = fields.Many2one('sale.order', string="Order origin")
    commission_total = fields.Monetary(string="Of which commission", store=True, compute="_compute_commission_total",
                                       help="Total commission value for the sale", tracking=True)
    associated_commission = fields.Boolean(string="Associated commission")

    @api.depends('order_line.price_commission')
    def _compute_commission_total(self):
        for order in self:
            amount_commission = 0.0
            for line in order.order_line:
                amount_commission += line.price_commission
            order.commission_total = amount_commission

    def _check_partner_country(self):
        """ The country on the contact form is mandatory to continue. The tax depends on the country """
        if not self.partner_id.country_id:
            raise ValidationError("No country is configured for the supplier. This configuration is mandatory "
                                  "to set an automatic tax when generating the quote "
                                  "of the 'commission' type")

    def _generate_commission_tax(self):
        """
        Search the tax for the supplier. If the supplier resides in France, the tax is 20%.
        If the supplier resides outside France, then no tax is applied
        """
        self._check_partner_country()
        commission_tax_id = self.env['account.tax'].search([('commission_tax', '=', True)])
        if not commission_tax_id or len(commission_tax_id) > 1:
            raise ValidationError(f"The configuration of a tax concerning the automatic creation of an estimate of "
                                  f"the type 'commission' is required to confirm the sale.\n"
                                  f"The company concerned by this configuration is {self.company_id.name}")
        if self.partner_id.country_id.phone_code != 33:
            return False
        if len(commission_tax_id) > 1:
            raise ValidationError("The tax for the automatic creation of the 'commission' type quote is "
                                  "unable to retrieve because there are at least two taxes configured")

        return [(4, commission_tax_id.id)]

    def _create_order_child(self):
        """
        Creation of a child sale if commission lines exist and addition of commission lines on
        the new sale for the manufacturer
        """
        for order in self:
            prepare_values = []
            company_user = self.env.user.company_id

            # Get amount commission. If commission create line in order line for child order
            for line in order.order_line:
                if line.price_commission > 0:
                    tax = order._generate_commission_tax()
                    # Prepare data for add commission line
                    commission_name = f"Commission pour {order.customer_id.name} sur {line.product_id.name or ''}. " \
                                      f"FC N°{order.customer_invoice_number or ''}"
                    prepare_values += [{
                        'name': commission_name,
                        'product_id': self.env.ref("sale_commission.kara_product_template_commission").id,
                        'product_uom_qty': 1,
                        'tax_id': tax if tax else False,
                        'price_unit': order.commission_total,
                        'company_id': company_user.id,
                    }]
            if len(prepare_values) > 0:
                if order.child_id:
                    # Replace all line
                    order.child_id.order_line = False
                    order.child_id.write({
                        'order_line': [(0, 0, data) for data in prepare_values],
                    })
                else:
                    # Create new order with commission line
                    child_id = order.copy({
                        'commission_order': True,
                        'order_origin_id': order.id,
                        'order_line': [(0, 0, data) for data in prepare_values],
                    })

                    # Affiliate order child into order
                    order.write({
                        'associated_commission': True,
                        'child_id': child_id.id,
                    })

    def action_quotation_send(self):
        """ Surcharge wizard to compose an email for change default mail template """
        res = super(SaleOrder, self).action_quotation_send()
        if not self.env.context.get('proforma') and self.state not in ('sale', 'done'):
            if self.trading_business and not self.commission_order:
                supplier_mail_template = self.env['ir.config_parameter'].sudo().\
                    get_param('custom_sale.supplier_mail_template_id', default=False)
                res['context'].update({
                    'default_use_template': bool(supplier_mail_template),
                    'default_template_id': int(supplier_mail_template) if supplier_mail_template else None,
                })

        return res
