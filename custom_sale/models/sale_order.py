# -*- coding: utf-8 -*-
import pytz
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def _get_supplier_id_domain(self):
        """ Allows you to search only for contacts with the supplier label """
        domain = []
        if self.env.company.trading_business:
            category_supplier = self.env.ref('custom_sale.kara_res_partner_category_supplier', False)
            if category_supplier:
                domain = [('category_id.id', '=', category_supplier.id)]
        return domain

    # @api.model
    def _get_customer_id_domain(self):
        """ Allows you to search only for contacts with the customer label """
        category_customer = self.env.ref('custom_sale.kara_res_partner_category_customer', False)
        if category_customer:
            return [('category_id.id', '=', category_customer.id)]

    trading_business = fields.Boolean(string="Trading business", related="company_id.trading_business")
    supplier_order = fields.Boolean(string="Supplier order", store=True, compute="_compute_supplier_order")

    supplier_id = fields.Many2one(
        'res.partner', string="Supplier", help="Industrial or warehouse", domain=_get_supplier_id_domain, tracking=True
    )
    customer_id = fields.Many2one('res.partner', string="Final customer", domain=_get_customer_id_domain, tracking=True)

    state = fields.Selection(
        selection_add=[
            ('confirmed', "Order confirmed"), ('invoiced', "Delivered / Invoiced"), ('payed', "Payed")
        ]
    )

    custom_report_name = fields.Char(string="PDF report name", store=True,
                                     help="Name of the report that will be generated when printing the PDF. "
                                          "The letter corresponds to the status of the sale")
    e_supplier_quote = fields.Binary(string="Supplier quote",
                                     help="Adding a PDF file is useful for creating a document template "
                                          "for electronic signature")
    e_supplier_quote_filename = fields.Char(string="File name")

    e_supplier_quote_signed = fields.Binary(string="Quote",
                                            help="The quote signed electronically by the customer in PDF format")
    e_supplier_quote_filename_signed = fields.Char(string="File name")

    supplier_quote_signed = fields.Binary(string="Quote", help="Add a manually signed quote here")
    supplier_quote_filename_signed = fields.Char(string="File name")

    sign_template_id = fields.Many2one(comodel_name='sign.template', string="Template to signed", readonly=1,
                                       help="Model created from the file inserted in the field above. "
                                            "The link to the Signature module")
    sign_request_id = fields.Many2one(comodel_name='sign.request', string="Related document", readonly=1,
                                      help="Document related to the model. The value of this field is visible only if "
                                           "the document has been signed by the person concerned. "
                                           "The link to the Signature module")

    @api.depends('trading_business', 'commission_order')
    def _compute_supplier_order(self):
        """
        Allows you to know if it is a sale for the manufacturer in order to display the associated buttons and fields
        """
        for order in self:
            if order.trading_business and not order.commission_order:
                order.supplier_order = True

    def _get_sign_item_values(self, template_id):
        """ Builds the items for the electronic signature """
        element_position_id = self.env['report.element.position'].search([])
        values = []
        for element in element_position_id:
            values += [{
                'template_id': template_id.id,
                'responsible_id': 1,
                'type_id': element.sign_item_type_id.id,
                'name': element.name,
                'page': 1,
                'posX': element.posX,
                'posY': element.posY,
                'width': element.width,
                'height': element.height,
            }]
        return values

    def _generate_attachment(self, pdf_name, file_data):
        attachment_id = self.env['ir.attachment'].create({
            'name': pdf_name,
            'type': 'binary',
            'datas': file_data,
            'store_fname': pdf_name,
            'res_model': self._name,
            'res_id': self.ids[0],
            'mimetype': 'application/x-pdf',
        })
        return attachment_id.id

    def action_send_quote_signed(self):
        """ Opens a wizard to compose an email, with relevant mail template loaded by default """
        self.ensure_one()

        # Get partner mail template
        template_id = self.env['ir.config_parameter'].sudo(). \
            get_param('custom_sale.supplier_quote_signed_mail_template_id', default=False)
        template_id = int(template_id)

        attachment_ids = []
        if self.supplier_quote_signed or self.e_supplier_quote_signed:
            if self.supplier_quote_signed:
                attachment_ids.append(
                    self._generate_attachment(self.supplier_quote_filename_signed, self.supplier_quote_signed)
                )
            if self.e_supplier_quote_signed:
                attachment_ids.append(
                    self._generate_attachment(self.e_supplier_quote_filename_signed, self.e_supplier_quote_signed)
                )

        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'default_attachment_ids': [(6, 0, attachment_ids)],
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
        }

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def action_create_sign_template(self):
        """ Generates a document template to sign. The retrieved document is the supplier quote """
        self.ensure_one()
        if not self.e_supplier_quote:
            raise UserError("Please fill in a PDF document before continuing")

        # Create attachment
        attachment_id = self.env['ir.attachment'].create({
            'res_model': 'sale.order',
            'res_id': self.id,
            'name': self.e_supplier_quote_filename,
            'datas': self.e_supplier_quote,
            'mimetype': 'application/pdf',
        })

        # Create sign template
        template_id = self.env['sign.template'].create({
            'attachment_id': attachment_id.id,
            'authorized_ids': [(4, self.env.user.id)],
            'order_id': self.id,
            'active': True,
        })

        # Get sign template for order
        self.sign_template_id = template_id.id

        # Generate items fo sign template
        vals = self._get_sign_item_values(template_id)
        for value_dict in vals:
            self.env['sign.item'].create(value_dict)

    def _define_report_name(self, vals):
        """
        Allows to set a new name on PDF sales reports.
        Format Trading : first 3 letters of industrial-DDMMYY-order number (ex : KAR-D-161222-SO0001.pdf)
        """

        # Generate date_format for pdf name
        local_tz = self.env.user.tz
        date_now = datetime.now(pytz.timezone(local_tz))
        date_format = date_now.strftime("%d%m%Y")

        # Get initial partner
        partner_id = self.env['res.partner'].browse([vals['partner_id']]) if 'partner_id' in vals else self.partner_id
        partner_name = partner_id.name
        initial_partner = partner_name.upper()[:3]

        # Get order name
        name_order = vals['name'] if 'name' in vals else self.name

        # Get order state
        state_order = vals['state'] if 'state' in vals else self.state

        # Get company
        company_id = self.env['res.company'].browse([vals['company_id']]) if 'company_id' in vals else self.company_id

        # Generate new name depending on the stage of the sale and business company
        if not company_id.trading_business:
            status_order = "Devis" if state_order in ['draft', 'sent'] else "Commande"
            return f"{status_order} - {name_order.replace('/', '')}"

        status_order = "D" if state_order in ['draft', 'sent'] else "C"
        return f"{initial_partner}-{status_order}-{date_format}-{name_order.replace('/', '')}"

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

    @api.onchange('e_supplier_quote')
    def _onchange_e_supplier_quote(self):
        """ RAZ template to signed if user to delete supplier quote to signed electronically """
        if not self.e_supplier_quote:
            self.sign_template_id = False

    def action_confirm_supplier(self):
        """ """
        self._create_order_child()
        for record in self:
            record.write({'state': 'confirmed'})

    def action_invoiced(self):
        """ Allows you to change the status of the sale to 'Delivered / Invoiced' """
        for record in self:
            record.write({'state': 'invoiced'})

    def action_payed(self):
        """
        Allows you to change the status of the sale to 'Paid'.
        Also changes the status of the commission order to 'sale'
        """
        for record in self:
            record.write({'state': 'payed'})
            if record.child_id:
                record.child_id.write({'state': 'sale'})

    @api.model
    def create(self, vals):
        """ Surcharge create method """
        record = super(SaleOrder, self).create(vals)
        record['custom_report_name'] = self._define_report_name(vals)

        return record

    def write(self, vals):
        """ Surcharge write method """
        for record in self:
            if not self.env.context.get('external_update', False):
                if record.name or record.partner_id:
                    vals['custom_report_name'] = record._define_report_name(vals)

        return super(SaleOrder, self).write(vals)
