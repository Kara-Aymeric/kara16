# -*- coding: utf-8 -*-
import base64
import re
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PaymentReminderLine(models.Model):
    _name = "payment.reminder.line"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "Payment Reminder Line"
    _order = "id desc"

    name = fields.Char(
        string="Name",
        default=lambda self: _('New'),
        index='trigram',
        readonly=True,
        required=True,
        store=True,
        copy=False,
    )

    move_id = fields.Many2one(
        'account.move',
        string="Move",
        readonly=True,
        required=True,
        store=True,
        copy=False,
    )

    partner_id = fields.Many2one(
        'res.partner',
        string="Partner",
        compute="_compute_partner_id",
        readonly=True,
        store=True,
        copy=False,
    )

    invoice_date = fields.Date(
        string="Invoice date",
        compute="_compute_invoice_date",
        readonly=True,
        store=True,
        copy=False,
    )

    invoice_origin = fields.Char(
        string="Origin",
        compute="_compute_invoice_origin",
        readonly=True,
        store=True,
        copy=False,
    )

    payment_reminder_id = fields.Many2one(
        'payment.reminder',
        string="Level reminder",
        readonly=True,
        store=True,
        copy=False,
    )

    date_maturity = fields.Date(
        string='Due date',
        compute="_compute_date_maturity",
        readonly=True,
        store=True,
        copy=False,
    )

    date_reminder = fields.Date(
        string='Reminder date',
        compute="_compute_date_reminder",
        readonly=False,
        store=True,
        copy=False,
    )

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        compute="_compute_currency_id",
        readonly=True,
        store=True,
        copy=False,
    )

    amount_residual = fields.Monetary(
        string="Amount Due",
        compute="_compute_amount_residual",
        readonly=True,
        store=True,
        copy=False,
    )

    payment_term_id = fields.Many2one(
        'account.payment.term',
        string="Payment term",
        compute="_compute_payment_term_id",
        readonly=True,
        store=True,
        copy=False,
    )

    manual_reminder = fields.Boolean(
        string="Manual reminder",
        readonly=True,
        store=True,
        copy=False,
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        index=True,
        readonly=True,
        store=True,
        copy=False,
    )

    email_subject = fields.Char(
        string="Subject",
        help="Subject retrieved automatically from the associated payment condition. "
             "This subject will be sent at the time of the reminder",
        compute="_compute_email_subject",
        readonly=False,
        copy=False,
        store=True,
    )

    email_content = fields.Html(
        string="Content",
        help="Email retrieved automatically from the associated payment condition. "
             "This email will be sent at the time of the reminder",
        compute="_compute_email_content",
        readonly=False,
        copy=False,
        store=True,
    )

    cancel_payment_reminder = fields.Boolean(
        string="Cancel payment reminder",
        help="By activating this box, the sending of emails for this reminder will not be carried out.",
        readonly=False,
        store=True,
        copy=False,
    )

    state = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("sent", "Sent"),
            ("blocked", "Blocked"),
            ("canceled", "Canceled"),
            ("ghost", "Ghost"),
        ],
        string="State",
        tracking=True,
        readonly=True,
        store=True,
        copy=False,
    )

    invoice_payment_status = fields.Selection(
        selection=[
            ("unpaid", "Unpaid"),
            ("paid", "Paid"),
        ],
        string="Payment state",
        compute="_compute_invoice_payment_status",
        tracking=True,
        readonly=True,
        store=True,
        copy=False,
    )

    @api.depends('move_id', 'move_id.partner_id')
    def _compute_partner_id(self):
        """ Compute partner """
        for line in self:
            if line.move_id and line.move_id.partner_id:
                line.partner_id = line.move_id.partner_id.id or False

    @api.depends('move_id', 'move_id.invoice_date')
    def _compute_invoice_date(self):
        """ Compute invoice date """
        for line in self:
            if line.move_id:
                line.invoice_date = line.move_id.invoice_date

    @api.depends('move_id', 'move_id.invoice_origin')
    def _compute_invoice_origin(self):
        """ Compute invoice origin """
        for line in self:
            if line.move_id:
                line.invoice_origin = line.move_id.invoice_origin

    @api.depends('move_id', 'move_id.invoice_date_due')
    def _compute_date_maturity(self):
        """ Compute invoice date due """
        for line in self:
            if line.move_id:
                line.date_maturity = line.move_id.invoice_date_due

    @api.depends('payment_reminder_id', 'date_maturity')
    def _compute_date_reminder(self):
        """ Compute date reminder """
        for line in self:
            date_reminder = False
            if line.payment_reminder_id and line.date_maturity:
                if line.payment_reminder_id.mail_template_id:
                    date_reminder = line.date_maturity + timedelta(days=line.payment_reminder_id.days)

            line.date_reminder = date_reminder

    @api.depends('move_id', 'move_id.currency_id')
    def _compute_currency_id(self):
        """ Compute currency """
        for line in self:
            if line.move_id and line.move_id.currency_id:
                line.currency_id = line.move_id.currency_id.id

    @api.depends('move_id', 'move_id.amount_residual')
    def _compute_amount_residual(self):
        """ Compute amount residual """
        for line in self:
            if line.move_id:
                line.amount_residual = line.move_id.amount_residual

    @api.depends('move_id', 'move_id.invoice_payment_term_id')
    def _compute_payment_term_id(self):
        """ Compute payment term id """
        for line in self:
            payment_term_id = False
            if line.move_id and line.move_id.invoice_payment_term_id:
                payment_term_id = line.move_id.invoice_payment_term_id
            line.payment_term_id = payment_term_id.id

    def _replace_label_for_email(self, html_content):
        """ Replace labels in HTML content for email """
        label_vals = {
            '#nomclient': self.partner_id.name,
            '#numerofacture': self.move_id.name,
            '#montant': str(self.move_id.amount_total),
            '#montantdu': str(self.amount_residual),
            '#datefacture': self.invoice_date.strftime("%d/%m/%Y") if self.invoice_date else "",
            '#dateecheance': self.date_maturity.strftime("%d/%m/%Y") if self.date_maturity else "",
        }

        for label, value in label_vals.items():
            html_content = html_content.replace(label, str(value))

        return html_content

    @api.depends('payment_term_id', 'payment_reminder_id', 'move_id', 'partner_id')
    def _compute_email_subject(self):
        """ Compute email subject """
        for line in self:
            email_subject = False
            if line.payment_term_id and line.payment_reminder_id and line.move_id:
                level = line.payment_reminder_id.sequence
                if level == 1:
                    email_subject = line._replace_label_for_email(line.payment_term_id.email_subject_x1) \
                        if line.payment_term_id.payment_reminder_id1 else False
                elif level == 2:
                    email_subject = line._replace_label_for_email(line.payment_term_id.email_subject_x2) \
                        if line.payment_term_id.payment_reminder_id2 else False
                elif level == 3:
                    email_subject = line._replace_label_for_email(line.payment_term_id.email_subject_x3) \
                        if line.payment_term_id.payment_reminder_id3 else False
            line.email_subject = email_subject

    @api.depends('payment_term_id', 'payment_reminder_id', 'move_id', 'partner_id')
    def _compute_email_content(self):
        """ Compute email content """
        for line in self:
            email_content = False
            if line.payment_term_id and line.payment_reminder_id:
                level = line.payment_reminder_id.sequence
                if level == 1:
                    email_content = line._replace_label_for_email(line.payment_term_id.email_content_x1) \
                        if line.payment_term_id.payment_reminder_id1 else False
                elif level == 2:
                    email_content = line._replace_label_for_email(line.payment_term_id.email_content_x2) \
                        if line.payment_term_id.payment_reminder_id2 else False
                elif level == 3:
                    email_content = line._replace_label_for_email(line.payment_term_id.email_content_x3) \
                        if line.payment_term_id.payment_reminder_id3 else False
            line.email_content = email_content

    @api.depends('move_id', 'move_id.payment_state')
    def _compute_invoice_payment_status(self):
        """ Compute invoice payment status """
        for line in self:
            payment_state = "unpaid"
            if line.move_id:
                if line.move_id.payment_state in ["in_payment", "paid"]:
                    payment_state = "paid"

            line.invoice_payment_status = payment_state
            if line.state == "sent" and line.invoice_payment_status == "paid":
                line.state = "blocked"
            if line.state in ["pending", "ghost"] and line.invoice_payment_status == "paid":
                line.unlink()

    def _send_payment_reminder_mail(self, payment_reminder_id, subject, body, move_id):
        """ Send mail to customer """
        # Get mail template id
        mail_template_id = payment_reminder_id.mail_template_id
        if not mail_template_id:
            raise ValidationError(
                _("It is necessary to have an email template configured into payment reminder")
            )

        # Check info mail template
        email_from = mail_template_id.email_from
        partner_to = mail_template_id.partner_to
        if not email_from and not partner_to:
            raise ValidationError(
                _("No sender or recipient configured into email template to payment reminder")
            )

        # Get PDF invoice if option is active
        attachment_id = False
        if payment_reminder_id.attach_invoice:
            invoice_report = self.env['ir.actions.report']._render_qweb_pdf("account.account_invoices", move_id.id)[0]
            invoice_report = base64.b64encode(invoice_report)
            invoice_name = f"{move_id.name.replace('/', '_')}.pdf"
            attachment_id = self.env['ir.attachment'].create({
                'name': invoice_name,
                'type': 'binary',
                'datas': invoice_report,
                'res_model': 'account.move',
                'res_id': move_id.id,
                'mimetype': 'application/pdf'
            })

        # Prepare email data
        email_values = {
            'subject': subject,
            'body_html': body,
            'attachment_ids': [(6, 0, [attachment_id.id])] if attachment_id else False,
        }

        # Send mail
        email_sent = mail_template_id.send_mail(self.id, True, email_values=email_values)
        mail_id = self.env['mail.mail'].browse([email_sent])
        if mail_id:
            # Get state
            state_value = ""
            for key, val in self.env['mail.mail']._fields['state']._description_selection(self.env):
                if mail_id.state in key:
                    state_value = val
                    break

            # Prepare body message for chatter
            body_message = """
            <b>Statut :</b> """+state_value+"""<br/><br/>
            <b>Sujet : </b>"""+mail_id.subject+"""<br/>
            -----
            """+mail_id.body_html

            # Add info into chatter
            self.message_post(body=body_message)

    def _get_invoice_not_payed(self, company_ids):
        """ Get invoice not payed for check payment reminder """
        domain = [
            ('state', '=', "posted"),
            ('move_type', '=', "out_invoice"),
            ('payment_state', 'not in', ["in_payment", "paid", "reversed"]),
            ('company_id', 'in', company_ids.ids),
        ]
        return self.env['account.move'].search(domain)

    def _create_partner_reminder_history(self):
        """ Create history into partner profile """
        history_id = self.env['payment.reminder.history'].create({
            'partner_id': self.partner_id.parent_id.id if self.partner_id.parent_id else self.partner_id.id,
            'invoice_id': self.move_id.id,
            'mail_reminder_date': fields.date.today(),
            'payment_reminder_line_id': self.id,
        })

        return history_id

    def action_force_payment_reminder(self):
        """ Force end payment reminder """
        self.ensure_one()
        payment_reminder_id = self.payment_reminder_id
        level_reminder = payment_reminder_id.sequence
        next_payment_reminder_id = self.env['payment.reminder'].search([('sequence', '=', level_reminder + 1)])
        self._send_payment_reminder_mail(payment_reminder_id, self.email_subject, self.email_content, self.move_id)
        self.move_id.message_post(body=_("Payment reminder email sent for %s", self.payment_reminder_id.name))
        self.message_post(body=_("Manual sending of the reminder by email carried out"))
        self.write({
            'date_reminder': fields.Date.today(),
            'state': "sent",
        })
        history_id = self._create_partner_reminder_history()
        if history_id:
            self.message_post(body=_("History partner created"))
        if next_payment_reminder_id and not self.partner_id.no_payment_reminder:
            if not self.sudo().search([
                ('move_id', '=', self.move_id.id), ('payment_reminder_id', '=', next_payment_reminder_id.id)
            ]):
                self.copy({
                    'move_id': self.move_id.id,
                    'payment_reminder_id': next_payment_reminder_id.id,
                    'state': "pending",
                })

    @api.model
    def _check_clear_payment_reminder(self):
        """ Clear payment reminder line if invoice is paid and state line is pending """
        for line in self.env['payment.reminder.line'].sudo().search([
            ('state', '=', "pending", "ghost"),
            ('invoice_payment_status', '=', 'paid')]
        ):
            line.unlink()

    @api.model
    def _check_payment_reminder(self):
        """ """
        company_ids = self.env['res.company'].search([('is_payment_reminder', '=', True)])
        if company_ids:
            # For first CRON. After it's state change who generate first payment reminder
            invoice_ids = self._get_invoice_not_payed(company_ids)
            for invoice in invoice_ids:
                if not invoice.payment_reminder_line:
                    invoice._create_payment_reminder_line(manual_reminder=True)

            for line in self.env['payment.reminder.line'].sudo().search([
                ('state', 'in', ['pending', 'blocked']),
                ('invoice_payment_status', '=', 'unpaid'),
                ('manual_reminder', '=', False)]
            ):
                today_date = datetime.today().date()
                payment_reminder_id = line.payment_reminder_id
                level_reminder = payment_reminder_id.sequence
                next_payment_reminder_id = self.env['payment.reminder'].search([('sequence', '=', level_reminder+1)])
                if line.date_reminder == today_date:
                    if line.state == 'pending':
                        # Send mail to customer
                        line._send_payment_reminder_mail(
                            payment_reminder_id, line.email_subject, line.email_content, line.move_id
                        )
                        line.move_id.message_post(
                            body=_("Payment reminder email sent for %s", payment_reminder_id.name)
                        )
                        line.message_post(body=_("Automatic sending of the reminder by email carried out"))
                        line.write({
                            'state': "sent",
                        })
                        history_id = line._create_partner_reminder_history()
                        if history_id:
                            line.message_post(body=_("History partner created"))
                    if line.state in ('pending', 'blocked'):
                        if next_payment_reminder_id and not line.partner_id.no_payment_reminder:
                            if not self.sudo().search([
                                ('move_id', '=', line.move_id.id),
                                ('payment_reminder_id', '=', next_payment_reminder_id.id)
                            ]):
                                line.copy({
                                    'move_id': line.move_id.id,
                                    'payment_reminder_id': next_payment_reminder_id.id,
                                    'state': "pending",
                                })

    def action_view_payment_reminder_line(self):
        self.ensure_one()
        context = dict(self.env.context)

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'payment.reminder.line',
            'views': [(self.env.ref('custom_payment_reminder.view_payment_reminder_line_form').id, 'form')],
            'res_id': self.id,
            'target': 'current',
            'context': context,
        }

    def action_cancel(self):
        """ Cancel payment reminder """
        self.ensure_one()
        self.write({'state': "canceled"})

    def action_pending(self):
        """ Pending payment reminder """
        self.ensure_one()
        self.write({'state': "pending"})

    def write(self, vals):
        """ Surcharge write method """
        for line in self:
            if vals.get('cancel_payment_reminder', False):
                vals['state'] = "blocked"

        return super(PaymentReminderLine, self).write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """ Surcharge create method """
        for vals in vals_list:
            if vals.get('name', _("New")) == _("New"):
                payment_reminder_id = self.env['payment.reminder'].browse([vals.get('payment_reminder_id', False)])
                move_id = self.env['account.move'].browse([vals.get('move_id', False)])
                sequence = payment_reminder_id.sequence if payment_reminder_id else False
                move_name = move_id.name if move_id else False
                vals['name'] = _("RP%s_%s", sequence, move_name) or _("New")

        return super().create(vals_list)
