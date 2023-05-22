# -*- coding: utf-8 -*-
{
    'name': 'Woo user connector',
    'version': '16.0.23.05.22',
    'category': 'Sales/Sales',
    'summary': """Facilite la connexion concernant les agents et leur client entre WooCommerce et Odoo pour Agorane""",
    'description': """Facilite la connexion concernant les agents et leur client entre WooCommerce et Odoo pour Agorane""",
    'website': 'https://hennet-solutions.fr',
    'license': 'LGPL-3',
    'depends': ['base', 'sale'],
    'data': [
        # Views
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
        'views/res_users_views.xml',
    ],
}
