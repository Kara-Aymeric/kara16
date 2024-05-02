# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_reminder_line = fields.One2many(
        'payment.reminder.line',
        'move_id',
        string="Payment reminder",
        copy=False,
        readonly=False
    )

    def _create_payment_reminder_line(self, manual_reminder=False):
        """ Create record for next payment reminder """
        if not self.partner_id.no_payment_reminder:
            payment_reminder_id = False
            payment_term_id = self.invoice_payment_term_id
            if payment_term_id:
                payment_reminder_id = (payment_term_id.payment_reminder_id1
                                       or payment_term_id.payment_reminder_id2
                                       or payment_term_id.payment_reminder_id3)

            if payment_reminder_id and self.company_id.id == payment_reminder_id.company_id.id:

                # Create payment reminder line
                vals = {
                    'move_id': self.id,
                    'payment_reminder_id': payment_reminder_id.id,
                    'manual_reminder': manual_reminder,
                }
                return self.payment_reminder_line.create(vals)
            return False
        return False

    def write(self, vals):
        """ Surcharge write method """
        res = super(AccountMove, self).write(vals)
        for move in self:
            if 'state' in vals:
                if move.company_id and move.company_id.is_payment_reminder:
                    if vals.get('state', False) == 'posted':
                        payment_reminder_line_id = move._create_payment_reminder_line()
                        if payment_reminder_line_id:
                            msg = _("Forecast reminder '%s' created", payment_reminder_line_id.payment_reminder_id.name)
                            move.message_post(body=msg)

                    if vals.get('state', False) in ['draft', 'cancel']:
                        if move.payment_reminder_line:
                            for line in move.payment_reminder_line.filtered(lambda x: x.state == 'pending'):
                                line.write({
                                    'date_reminder': False,
                                    'state': 'canceled',
                                })
                                move.message_post(
                                    body=_("Cancel reminder '%s'", line.payment_reminder_id.name)
                                )

        return res
