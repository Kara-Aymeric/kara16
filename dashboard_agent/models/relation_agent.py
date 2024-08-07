# -*- coding: utf-8 -*-
import datetime
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class RelationAgent(models.Model):
    _name = 'relation.agent'
    _rec_name = 'godfather_id'
    _description = "Relation agent"

    godfather_id = fields.Many2one(
        'res.users',
        string="Godfather",
    )
    godson_id = fields.Many2one(
        'res.users',
        string="Godson",
    )
    start_date = fields.Date(
        string="Start date",
        default=datetime.datetime.today()
    )
    end_date = fields.Date(
        string="End date",
        compute="_compute_end_date",
        store=True,
        readonly=False
    )
    commission = fields.Float(string="Commission")
    is_expired = fields.Boolean(
        string="Is expired", copy=False, compute="_compute_is_expired", store=True
    )
    active = fields.Boolean(
        default=True,
        help="By unchecking the active field, you can hide a record without deleting it."
    )

    @api.depends("end_date")
    def _compute_is_expired(self):
        """ Compute is expired """
        for record in self:
            is_expired = False
            if record.end_date:
                if fields.Date.today() > record.end_date:
                    is_expired = True
            record.is_expired = is_expired

    @api.depends('start_date')
    def _compute_end_date(self):
        """ Get delta set in general settings for calculate end_date """
        for record in self:
            end_date = False
            param = self.env['ir.config_parameter'].sudo()
            sponsorship_duration = param.get_param('dashboard_agent.sponsorship_duration')

            if sponsorship_duration and record.start_date:
                end_date = record.start_date + relativedelta(days=int(sponsorship_duration))

            record.end_date = end_date

