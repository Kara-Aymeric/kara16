# -*- coding: utf-8 -*-
import datetime
from odoo import models, fields


class SynchronizationCommissionHistory(models.Model):
    _name = "synchronization.commission.history"
    _order = "id desc"
    _description = "Synchronization history"

    date = fields.Datetime(string="Synchronization date", default=datetime.datetime.now())
    type = fields.Selection([('automatic', 'Automatic'), ('manual', 'Manual')])
    name = fields.Char(string="Name")
    message = fields.Text(string="Message")
    sync_ok = fields.Boolean(string="Update done")
