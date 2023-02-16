# -*- coding: utf-8 -*-
{
    'name': 'Vente personnalisé',
    'version': '16.0.23.02.08',
    'category': 'Sales/Sales',
    'summary': """Personnalisation du module Vente pour Kara""",
    'description': """Personnalisation du module Vente pour Kara""",
    'website': 'https://hennet-solutions.fr',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'delivery',
        'crm',
        'sale',
        'sign',
        'sale_commission',
        'show_hide_menu_multi_company_app'],
    'data': [
        # Data
        'data/mail_template_data.xml',
        'data/report_element_position_data.xml',
        'data/res_partner_category_data.xml',
        # Security
        'security/ir.model.access.csv',
        # Report
        'report/sale_report_templates.xml',
        # Views
        'views/crm_views.xml',
        'views/product_views.xml',
        'views/report_element_position_views.xml',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_category_views.xml',
        'views/sale_order_views.xml',
        'views/sign_views.xml',
    ],
}
