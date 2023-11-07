# -*- coding: utf-8 -*-
{
    "name": "Commission agent",
    "summary": """
    Module qui permet de gérer les commissions des agents et d'afficher le montant des commissions générées
    """,
    "description": """ """,
    "author": "Kevin HENNION",
    'website': 'https://hennet-solutions.fr',
    'license': 'LGPL-3',
    'category': 'Sales/Sales',
    "version": "16.0.23.11.07",
    "installable": True,
    "depends": ['base', 'dashboard_agent'],
    "data": [
        # Security
        "security/ir.model.access.csv",

        # Views
        "views/commission_agent_rule_views.xml",
        "views/res_groups_views.xml",
        "views/synchronization_commission_history_views.xml",
        # "wizard/synchronise_salary_manually.xml",
        "views/commission_agent_menus.xml",

        # Wizard
        # "wizard/commission_details_wizard_views.xml",
        # "wizard/commission_rule_wizard_views.xml",
    ],
}
