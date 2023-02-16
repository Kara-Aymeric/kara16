# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    access_commission = fields.Boolean(string="Allows the use of sales commissions")
