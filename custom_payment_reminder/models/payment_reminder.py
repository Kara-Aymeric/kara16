# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class PaymentReminder(models.Model):
    _name = "payment.reminder"
    _description = "Payment Reminder"

    name = fields.Char(
        string="Name",
        readonly=True,
    )

    days = fields.Integer(
        string="Days",
        help="You can enter a positive or negative value here",
    )

    mail_template_id = fields.Many2one(
        "mail.template",
        string="Mail Template",
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        default=lambda self: self.env.company,
        index=True,
    )

    active = fields.Boolean(
        default=True,
        help="By unchecking the active field, you can hide a record without deleting it."
    )

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
