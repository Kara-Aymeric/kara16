# -*- coding: utf-8 -*-
{
    'name': 'Dashboard agent',
    'version': '16.0.23.05.05',
    'category': 'Sales/Sales',
    'summary': 'Tableau de bord agent',
    'description': """
        Ce module permet d'avoir un tableau de bord agent en tant que application Odoo afin de faciliter la création 
        et le suivi des ventes.
    """,
    'website': 'https://hennet-solutions.fr',
    'license': 'LGPL-3',
    'depends': ['account', 'sale'],
    'data': [
        # Data
        # 'data/product_data.xml',

        # Report
        # 'report/sale_report_templates.xml',

        # Security
        'security/res_groups.xml',
        # 'security/ir.model.access.csv',

        # Views
        'views/res_config_settings_views.xml',
        'views/sale_order_views.xml',
        'views/dashboard_agent_menus.xml',
    ],
}
