# -*- coding: utf-8 -*-
from odoo import models, fields, _


class SynchroniseSalaryManually(models.TransientModel):
    _name = "synchronise.salary.manually"
    _description = "Wizard to execute manually synchronisation of salary"

    user_id = fields.Many2one("res.users", string="User", required=True, default=lambda self: self.env.user)
    sync_date_start = fields.Datetime(string="Begin date")
    sync_date_end = fields.Datetime(string="End date")
    comment = fields.Text(string="Comment", required=True)

    def action_synchronise(self):
        self.env['commission.agent'].calculate_commission(manual=True, comment=self.comment)
