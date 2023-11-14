# -*- coding: utf-8 -*-
from odoo import models, fields, _


class SyncManuallyWizard(models.TransientModel):
    _name = "sync.manually.wizard"
    _description = "Wizard to execute manually synchronization for calculation commission agent"

    user_id = fields.Many2one("res.users", string="User", required=True, default=lambda self: self.env.user)
    comment = fields.Char(string="Comment")

    def action_synchronize(self):
        """ Force synchronization from button into modal window """
        print("Force sync")
        self.env['commission.agent'].action_synchronize(type_sync="manual", comment=self.comment)
