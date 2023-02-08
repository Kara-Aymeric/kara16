# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ReportElementPosition(models.Model):
    _name = 'report.element.position'

    name = fields.Char(string="Name", help="Name displayed on PDF")
    sign_item_type_id = fields.Many2one('sign.item.type', string="Item type",
                                        help="Type of field to insert in the PDF document")
    posX = fields.Float(digits=(4, 3), string="Position X", required=True)
    posY = fields.Float(digits=(4, 3), string="Position Y", required=True)
    width = fields.Float(digits=(4, 3), string="Width", required=True)
    height = fields.Float(digits=(4, 3), string="Height", required=True)
    active = fields.Boolean(default=True, tracking=True,
                            help="By unchecking the active field, you can hide a report element position "
                                 "without deleting it.")
