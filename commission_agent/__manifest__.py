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
    "depends": ['base', 'dashboard_agent', 'custom_sale', 'sale'],
    "data": [
        # Data
        "data/commission_agent_rule_data.xml",
        "data/product_data.xml",
        "data/res_partner_category_data.xml",

        # Security
        "security/commission_agent_security.xml",
        "security/ir.model.access.csv",

        # Views
        "views/account_move_views.xml",
        "views/commission_agent_rule_views.xml",
        "views/commission_agent_views.xml",
        "views/sale_order_views.xml",
        "views/synchronization_commission_history_views.xml",

        # Wizard
        "wizard/sync_manually_wizard_views.xml",

        # Menu
        "views/commission_agent_menus.xml",

    ],
}
