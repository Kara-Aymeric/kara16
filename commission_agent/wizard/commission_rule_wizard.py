# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CommissionRuleWizard(models.TransientModel):
    _name = 'commission.rule.wizard'
    _description = "Commission rule wizard"

    user_id = fields.Many2one(
        'res.users',
        string="Salespeople"
    )
    commission_rule_ids = fields.Many2many(
        'commission.salespeople.rule',
        string="Rules",
    )
    rule_assigned = fields.Char(
        string="Rules assigned",
    )

    @api.onchange('user_id')
    def _onchange_user_id(self):
        """ Propose rule not assigned to salespeople """
        if self.user_id:
            domain = [('id', 'not in', eval(self.rule_assigned))]
            return {'domain': {'commission_rule_ids': domain}}

    def _assign_rule(self, user_id):
        """ Assign rule to salespeople """
        rules_name = []
        for rule in self.commission_rule_ids:
            rule.write({
                'salesperson_ids': [(4, user_id)]
            })
            rules_name.append(rule.name)

        return rules_name

    def action_add_salespeople_commission_rule(self):
        """ Allows to associated one or many rules to salespeople """
        ctx = self.env.context
        user_id = ctx.get('default_user_id', False)
        res_id = ctx.get('default_res_id', False)

        if not user_id or not res_id:
            raise ValidationError(
                _("A problem has been encountered. Check the presence of a user linked to the employee file. "
                  "Please contact your administrator!")
            )

        # Add rule to salespeople
        new_rules = self._assign_rule(user_id)
        if len(new_rules) > 0:
            # Add info into chatter
            new_rule_str = "<br/>- ".join(new_rules)
            body_message = _("<b>Rule assigned : </b><br/>- %s", new_rule_str)
            self.env['hr.employee'].browse([res_id]).message_post(body=body_message)
