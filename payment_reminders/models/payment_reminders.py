# -*- coding: utf-8 -*-
# © 2018-Today Aktiv Software (http://www.aktivsoftware.com).
# Part of AktivSoftware See LICENSE file for full copyright
# and licensing details.

from datetime import datetime, timedelta

from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class PaymentReminders(models.Model):
    _name = "payment.reminders"
    _description = "Payment Reminders"

    name = fields.Char(
        readonly=True,
    )
    reminder_selection = fields.Selection(
        [("before_due_date", "Before Due Date"), ("after_due_date", "After Due Date")],
        required=True,
    )
    days = fields.Integer(
        help="Only takes Positive values for days",
        default=0,
    )
    mail_template_id = fields.Many2one(
        "mail.template",
        string="Mail Template",
        required=True,
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env["res.company"]._company_default_get(
            "payment.reminders"
        ),
        index=True,
        required=True,
    )

    @api.model
    def create(self, vals):
        """Override create method to apply sequence."""
        vals["name"] = self.env["ir.sequence"].next_by_code("payment.reminders") or "/"
        return super(PaymentReminders, self).create(vals)

    @api.model
    def check_payment_due_date(self):
        """This method will call when scheduler will executed"""
        # Fetch only those payment reminders records which company's
        # payment reminder is enabled.
        payment_reminder_recs = self.sudo().search(
            [("company_id.is_payment_reminder", "=", True)]
        )
        all_invoice_recs = (
            self.env["account.move"]
            .sudo()
            .search([("state", "=", "posted"), ("move_type", "=", "out_invoice")])
        )
        # Fetch current date
        today_date = datetime.today().date()
        for payment_reminder_rec in payment_reminder_recs:
            company_id = payment_reminder_rec.company_id.id
            if payment_reminder_rec.reminder_selection == "before_due_date":
                due_date = today_date + timedelta(days=payment_reminder_rec.days)
                # date converted into odoo system's date format to filter
                # invoices with that due date.
                email_subject = (
                    "Notification: "
                    + str(payment_reminder_rec.days)
                    + " days remaining for due date"
                )

            else:
                due_date = today_date - timedelta(days=payment_reminder_rec.days)
                # date converted into odoo system's date format to filter
                # invoices with that due date.
                email_subject = (
                    "Notification: "
                    + str(payment_reminder_rec.days)
                    + " days had been passed for due date"
                )
            # Filter invoices with current payment reminder's company_id and
            # due date.
            invoice_recs = all_invoice_recs.with_context(
                due_date=due_date, company_id=company_id
            ).filtered(
                lambda invoice: invoice.invoice_date_due == invoice._context["due_date"]
                and invoice.company_id.id == invoice._context["company_id"]
            )

            for invoice_rec in invoice_recs:
                # Send mail to customer.
                template = payment_reminder_rec.mail_template_id.sudo().with_context(
                    subject=email_subject,
                    customer=invoice_rec.partner_id.name,
                    invoice_number=invoice_rec.name,
                    due_date=invoice_rec.invoice_date_due,
                    amount_due=invoice_rec.amount_residual,
                    remaining_days=payment_reminder_rec.days,
                )
                template.send_mail(payment_reminder_rec.id, force_send=True)
                invoice_rec.partner_id.partner_payment_reminders_ids = [
                    (
                        0,
                        0,
                        {
                            "partner_id": invoice_rec.partner_id.id,
                            "invoice_id": invoice_rec.id,
                            "mail_date": today_date.strftime(
                                DEFAULT_SERVER_DATE_FORMAT
                            ),
                            "email_template_id": payment_reminder_rec.mail_template_id.id,
                            "due_date": invoice_rec.invoice_date_due,
                            "company_id": invoice_rec.company_id.id,
                        },
                    )
                ]
