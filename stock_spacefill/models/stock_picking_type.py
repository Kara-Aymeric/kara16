#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:copyright: (c) 2022 irokoo
:license: AGPLv3, see LICENSE for more details

"""
from odoo import api, fields, models, _


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    is_archive_by_default = fields.Boolean(string='Archive by default ?')
    only_manage_by_spacefill = fields.Boolean('Only manage by Spacefill', related='warehouse_id.is_exported', store=True)
    