# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models


class PaymentReminderLine(models.Model):
    _name = "payment.reminder.line"
    _inherit = ["portal.mixin", "mail.thread", "mail.activity.mixin", "utm.mixin"]
    _description = "Payment Reminder Line"
    _order = "id desc"

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
        readonly=True,
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

    def action_force_payment_reminder(self):
        """ Force end payment reminder """
        self.ensure_one()
        pass

    @api.model
    def _check_payment_reminder(self):
        pass

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
