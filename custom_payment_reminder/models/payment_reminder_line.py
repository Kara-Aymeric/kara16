# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, _


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
        copy=False,
        store=True,
    )

    email_content = fields.Html(
        string="Content",
        help="Email retrieved automatically from the associated payment condition. "
             "This email will be sent at the time of the reminder",
        copy=False,
        store=True,
    )

    state = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("sent", "Sent"),
            ("canceled", "Canceled"),
        ],
        string="State",
        default="pending",
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

    def _get_invoice_not_payed(self, company_ids):
        """ Get invoice not payed for check payment reminder """
        domain = [
            ('state', '=', "posted"),
            ('move_type', '=', "out_invoice"),
            ('payment_state', 'not in', ["in_payment", "paid", "reversed"]),
            ('company_id', 'in', company_ids.ids),
        ]
        return self.env['account.move'].search(domain)

    def action_force_payment_reminder(self):
        """ Force end payment reminder """
        self.ensure_one()
        pass

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

            for line in self:
                today_date = datetime.today().date()
                payment_reminder_id = line.payment_reminder_id
                level_reminder = payment_reminder_id.sequence
                next_payment_reminder_id = self.env['payment.reminder'].search([('sequence', '=', level_reminder+1)])
                if line.date_reminder == today_date and line.state == 'pending':
                    # Send mail to customer
                    success_send_mail = line._send_payment_reminder_mail()
                    if success_send_mail:
                        line.write({
                            'state': "sent",
                        })
                        msg = _("Payment reminder email sent for %s", payment_reminder_id.name)
                        line.move_id.message_post(body=msg)
                        if next_payment_reminder_id and not line.partner_id.no_payment_reminder:
                            line.copy({
                                'payment_reminder_id': next_payment_reminder_id.id,
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

    # @api.model
    # def _check_payment_reminder(self):
    #     """This method will call when scheduler will executed"""
    #     # Fetch only those payment reminders records which company's
    #     # payment reminder is enabled.
    #     payment_reminder_recs = self.sudo().search(
    #         [("company_id.is_payment_reminder", "=", True)]
    #     )
    #     all_invoice_recs = (
    #         self.env["account.move"]
    #         .sudo()
    #         .search([("state", "=", "posted"), ("move_type", "=", "out_invoice")])
    #     )
    #     # Fetch current date
    #     today_date = datetime.today().date()
    #     for payment_reminder_rec in payment_reminder_recs:
    #         company_id = payment_reminder_rec.company_id.id
    #         if payment_reminder_rec.reminder_selection == "before_due_date":
    #             due_date = today_date + timedelta(days=payment_reminder_rec.days)
    #             # date converted into odoo system's date format to filter
    #             # invoices with that due date.
    #             email_subject = (
    #                 "Notification: "
    #                 + str(payment_reminder_rec.days)
    #                 + " days remaining for due date"
    #             )
    #
    #         else:
    #             due_date = today_date - timedelta(days=payment_reminder_rec.days)
    #             # date converted into odoo system's date format to filter
    #             # invoices with that due date.
    #             email_subject = (
    #                 "Notification: "
    #                 + str(payment_reminder_rec.days)
    #                 + " days had been passed for due date"
    #             )
    #         # Filter invoices with current payment reminder's company_id and
    #         # due date.
    #         invoice_recs = all_invoice_recs.with_context(
    #             due_date=due_date, company_id=company_id
    #         ).filtered(
    #             lambda invoice: invoice.invoice_date_due == invoice._context["due_date"]
    #             and invoice.company_id.id == invoice._context["company_id"]
    #         )
    #
    #         for invoice_rec in invoice_recs:
    #             # Send mail to customer.
    #             template = payment_reminder_rec.mail_template_id.sudo().with_context(
    #                 subject=email_subject,
    #                 customer=invoice_rec.partner_id.name,
    #                 invoice_number=invoice_rec.name,
    #                 due_date=invoice_rec.invoice_date_due,
    #                 amount_due=invoice_rec.amount_residual,
    #                 remaining_days=payment_reminder_rec.days,
    #             )
    #             template.send_mail(payment_reminder_rec.id, force_send=True)
    #             invoice_rec.partner_id.partner_payment_reminders_ids = [
    #                 (
    #                     0,
    #                     0,
    #                     {
    #                         "partner_id": invoice_rec.partner_id.id,
    #                         "invoice_id": invoice_rec.id,
    #                         "mail_date": today_date.strftime(
    #                             DEFAULT_SERVER_DATE_FORMAT
    #                         ),
    #                         "email_template_id": payment_reminder_rec.mail_template_id.id,
    #                         "due_date": invoice_rec.invoice_date_due,
    #                         "company_id": invoice_rec.company_id.id,
    #                     },
    #                 )
    #             ]
