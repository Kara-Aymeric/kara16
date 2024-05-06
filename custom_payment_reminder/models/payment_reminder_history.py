# -*- coding: utf-8 -*-
from odoo import fields, models


class PaymentReminderHistory(models.Model):
    _name = "payment.reminder.history"
    _description = "Payment Reminder History"
    _order = "id desc"

    partner_id = fields.Many2one(
        "res.partner",
        string="Customer",
    )

    invoice_id = fields.Many2one(
        "account.move",
        string="Invoice",
    )

    mail_reminder_date = fields.Date(
        string="Mail reminder date",
        help="Date the reminder email was sent"
    )

    payment_reminder_line_id = fields.Many2one(
        "payment.reminder.line",
        string="Reminder detail"
    )

    def action_view_payment_reminder_line(self):
        self.ensure_one()
        context = dict(self.env.context)

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'payment.reminder.line',
            'views': [(self.env.ref('custom_payment_reminder.view_payment_reminder_line_form').id, 'form')],
            'res_id': self.payment_reminder_line_id.id,
            'target': 'current',
            'context': context,
        }
