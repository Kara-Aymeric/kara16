# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class PartnerTypology(models.Model):
    _name = "partner.typology"
    _description = "Partner Typology"
    _parent_name = "parent_id"
    _parent_store = True
    _rec_name = 'name'
    _order = 'complete_name'

    name = fields.Char(string="Name", index='trigram')
    code = fields.Char(string="Code", help="Allows to add prefix into reference to contact", required=True)
    complete_name = fields.Char(
        'Complete Name', compute='_compute_complete_name', recursive=True,
        store=True)
    parent_path = fields.Char(index=True, unaccent=False)
    parent_id = fields.Many2one('partner.typology', 'Parent Typology', index=True, ondelete='cascade')
    child_id = fields.One2many('partner.typology', 'parent_id', 'Child Typologies')

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for typology in self:
            if typology.parent_id:
                typology.complete_name = '%s / %s' % (typology.parent_id.complete_name, typology.name)
            else:
                typology.complete_name = typology.name

    @api.constrains('parent_id')
    def _check_typology_recursion(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive typologies.'))
