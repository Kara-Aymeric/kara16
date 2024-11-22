# -*- coding: utf-8 -*-
import re
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    selection = [('yes', 'Yes'), ('no', 'No')]

    # Logistic
    # Delivery schedule
    monday_morning = fields.Char(string="Monday morning")
    tuesday_morning = fields.Char(string="Tuesday morning")
    wednesday_morning = fields.Char(string="Wednesday morning")
    thursday_morning = fields.Char(string="Thursday morning")
    friday_morning = fields.Char(string="Friday morning")
    saturday_morning = fields.Char(string="Saturday morning")
    sunday_morning = fields.Char(string="Sunday morning")

    monday_afternoon = fields.Char(string="Monday afternoon")
    tuesday_afternoon = fields.Char(string="Tuesday afternoon")
    wednesday_afternoon = fields.Char(string="Wednesday afternoon")
    thursday_afternoon = fields.Char(string="Thursday afternoon")
    friday_afternoon = fields.Char(string="Friday afternoon")
    saturday_afternoon = fields.Char(string="Saturday afternoon")
    sunday_afternoon = fields.Char(string="Sunday afternoon")

    # Specificities
    need_tailgate = fields.Selection(selection=selection, string="Need tailgate", default='no')
    unloading_dock = fields.Selection(selection=selection, string="Unloading dock", default='no')
    semi_trailer = fields.Selection(selection=selection, string="Semi-trailer", default='no')
    van = fields.Selection(selection=selection, string="Van", default='no')
    pedestrian_street = fields.Selection(selection=selection, string="Pedestrian street", default='no')
    prior_authorisation = fields.Selection(selection=selection, string="Prior authorization required", default='no')
    appointment = fields.Selection(selection=selection, string="Appointment", default='no')
    pallet_exchange = fields.Selection(selection=selection, string="Pallet exchange", default='no')

    # Comments
    logistic_comment = fields.Html(string="Comment", translate=True)

    @api.constrains('phone', 'mobile')
    def _constrains_phone_mobile(self):
        """ Check if telephone number before save contact profile """
        if not self.phone and not self.mobile:
            raise ValidationError(
                "Merci de renseigner un numéro de téléphone."
            )

    def _check_schedule_format(self, data):
        """ Request format : 00h00 - 00h00 or 00H00 - 00H00 """
        match = re.match(
            r"^((0[0-9]|1[0-9]|2[0-3])([hH])[0-5][0-9]\s(-)\s(0[0-9]|1[0-9]|2[0-3])([hH])[0-5][0-9])$", data
        )
        if not match:
            raise ValidationError(
                "Pour les horaires de livraison, merci de respecter ce format : 00h00 - 00h00 ou 00H00 - 00H00"
            )

    @api.onchange('monday_morning')
    @api.constrains('monday_morning')
    def _onchange_constrains_monday_morning(self):
        if self.monday_morning and self.monday_morning.replace(" ", "") != '-':
            self._check_schedule_format(self.monday_morning)

    @api.onchange('tuesday_morning')
    @api.constrains('tuesday_morning')
    def _onchange_constrains_tuesday_morning(self):
        if self.tuesday_morning and self.tuesday_morning.replace(" ", "") != '-':
            self._check_schedule_format(self.tuesday_morning)

    @api.onchange('wednesday_morning')
    @api.constrains('wednesday_morning')
    def _onchange_constrains_wednesday_morning(self):
        if self.wednesday_morning and self.wednesday_morning.replace(" ", "") != '-':
            self._check_schedule_format(self.wednesday_morning)

    @api.onchange('thursday_morning')
    @api.constrains('thursday_morning')
    def _onchange_constrains_thursday_morning(self):
        if self.thursday_morning and self.thursday_morning.replace(" ", "") != '-':
            self._check_schedule_format(self.thursday_morning)

    @api.onchange('friday_morning')
    @api.constrains('friday_morning')
    def _onchange_constrains_friday_morning(self):
        if self.friday_morning and self.friday_morning.replace(" ", "") != '-':
            self._check_schedule_format(self.friday_morning)

    @api.onchange('saturday_morning')
    @api.constrains('saturday_morning')
    def _onchange_constrains_saturday_morning(self):
        if self.saturday_morning and self.saturday_morning.replace(" ", "") != '-':
            self._check_schedule_format(self.saturday_morning)

    @api.onchange('sunday_morning')
    @api.constrains('sunday_morning')
    def _onchange_constrains_sunday_morning(self):
        if self.sunday_morning and self.sunday_morning.replace(" ", "") != '-':
            self._check_schedule_format(self.sunday_morning)

    @api.onchange('monday_afternoon')
    @api.constrains('monday_afternoon')
    def _onchange_constrains_monday_afternoon(self):
        if self.monday_afternoon and self.monday_afternoon.replace(" ", "") != '-':
            self._check_schedule_format(self.monday_afternoon)

    @api.onchange('tuesday_afternoon')
    @api.constrains('tuesday_afternoon')
    def _onchange_constrains_tuesday_afternoon(self):
        if self.tuesday_afternoon and self.tuesday_afternoon.replace(" ", "") != '-':
            self._check_schedule_format(self.tuesday_afternoon)

    @api.onchange('wednesday_afternoon')
    @api.constrains('wednesday_afternoon')
    def _onchange_constrains_wednesday_afternoon(self):
        if self.wednesday_afternoon and self.wednesday_afternoon.replace(" ", "") != '-':
            self._check_schedule_format(self.wednesday_afternoon)

    @api.onchange('thursday_afternoon')
    @api.constrains('thursday_afternoon')
    def _onchange_constrains_thursday_afternoon(self):
        if self.thursday_afternoon and self.thursday_afternoon.replace(" ", "") != '-':
            self._check_schedule_format(self.thursday_afternoon)

    @api.onchange('friday_afternoon')
    @api.constrains('friday_afternoon')
    def _onchange_constrains_friday_afternoon(self):
        if self.friday_afternoon and self.friday_afternoon.replace(" ", "") != '-':
            self._check_schedule_format(self.friday_afternoon)

    @api.onchange('saturday_afternoon')
    @api.constrains('saturday_afternoon')
    def _onchange_constrains_saturday_afternoon(self):
        if self.saturday_afternoon and self.saturday_afternoon.replace(" ", "") != '-':
            self._check_schedule_format(self.saturday_afternoon)

    @api.onchange('sunday_afternoon')
    @api.constrains('sunday_afternoon')
    def _onchange_constrains_sunday_afternoon(self):
        if self.sunday_afternoon and self.sunday_afternoon.replace(" ", "") != '-':
            self._check_schedule_format(self.sunday_afternoon)
