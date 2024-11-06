# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    stage_change_delta_ids = fields.One2many(
        "stage.change.delta", "lead_id", string="Stage change delta"
    )

    def _create_stage_change_delta(self, lead):
        """ Create stage change delta for lead """
        old_stage_id = False
        previous_record = self.env['stage.change.delta'].search([('lead_id', '=', lead.id)], order="id desc", limit=1)
        if previous_record and previous_record.stage_id:
            old_stage_id = previous_record.stage_id.id

        state_change_delta_id = self.env['stage.change.delta'].create({
            'date': fields.Datetime.now(),
            'stage_id': lead.stage_id.id,
            'old_stage_id': old_stage_id,
            'lead_id': lead.id,
            'user_id': self.env.user.id,
        })

    @api.model_create_multi
    def create(self, vals_list):
        """ Surcharge create method """
        leads = super().create(vals_list)
        for lead in leads:
            self._create_stage_change_delta(lead)

        return leads

    def write(self, vals):
        """ Surcharge write method """
        res = super().write(vals)
        if "stage_id" in vals:
            for lead in self:
                self._create_stage_change_delta(lead)

        return res
