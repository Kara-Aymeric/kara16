# -*- coding: utf-8 -*-
from odoo import api, fields, models


class CrmLead(models.Model):
    _inherit = "crm.lead"

    stage_tracking_ids = fields.One2many(
        "stage.tracking", "lead_id", string="Stage tracking"
    )

    pricelist_id = fields.Many2one(
        'product.pricelist', related="partner_id.property_product_pricelist"
    )

    partner_typology_id = fields.Many2one(
        'partner.typology', string="Typology", required=True,
        store=True, related="partner_id.partner_typology_id"
    )

    partner_typology_id2 = fields.Many2one(
        'partner.typology', string="Specificity",
        store=True, related="partner_id.partner_typology_id2"
    )

    def _create_stage_tracking(self, lead):
        """ Create stage tracking for lead """
        old_stage_id = False
        previous_record = self.env['stage.tracking'].search([('lead_id', '=', lead.id)], order="id desc", limit=1)
        if previous_record and previous_record.stage_id:
            old_stage_id = previous_record.stage_id.id

        stage_tracking_id = self.env['stage.tracking'].create({
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
            self._create_stage_tracking(lead)

        return leads

    def write(self, vals):
        """ Surcharge write method """
        res = super().write(vals)
        if "stage_id" in vals:
            for lead in self:
                self._create_stage_tracking(lead)

        return res
