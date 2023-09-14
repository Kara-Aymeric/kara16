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
    'depends': ['account', 'crm', 'sale', 'mail', 'custom_sale', 'sale_commission', 'woo_user_connector'],
    'data': [
        # Data
        'data/ir_module_category_data.xml',
        'data/mail_template_data.xml',
        'data/product_data.xml',

        # Report
        # 'report/sale_report_templates.xml',

        # Security
        'security/res_groups.xml',
        'security/ir.model.access.csv',

        # Views
        'views/account_move_views.xml',
        'views/crm_lead_views.xml',
        'views/product_template_views.xml',
        'views/relation_agent_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/dashboard_agent_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dashboard_agent/static/src/xml/*.xml',
        ],
    },
}
