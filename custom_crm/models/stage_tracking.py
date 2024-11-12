# -*- coding: utf-8 -*-
from odoo import api, fields, models


class StageTracking(models.Model):
    _name = "stage.tracking"
    _rec_name = "stage_id"
    _description = "Stage Tracking"

    date = fields.Date(string="Date")
    stage_id = fields.Many2one("crm.stage", string="New stage")
    old_stage_id = fields.Many2one("crm.stage", string="Old stage")
    lead_id = fields.Many2one("crm.lead", string="Lead")
    user_id = fields.Many2one("res.users", string="User")
    delta = fields.Integer(string="Delta (days)", compute="_compute_delta", store=True)

    @api.depends('date')
    def _compute_delta(self):
        """ Compute delta in days between previous date and date now """
        for record in self:
            previous_record = self.search([
                ('id', '<', record.id), ('lead_id', '=', record.lead_id.id)
            ], order="id desc", limit=1)
            old_date = previous_record.date if previous_record else None
            new_date = record.date
            if old_date and new_date:
                delta_days = (new_date - old_date).days
                record.delta = int(delta_days)
            else:
                record.delta = 0
