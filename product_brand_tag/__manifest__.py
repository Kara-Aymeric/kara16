# -*- coding: utf-8 -*-
{
    'name': 'Étiquette marques auto',
    'summary': """ Permet de cibler les marques achetés par les clients """,
    'description': """ Permet de cibler les marques achetés par les clients """,
    'version': "16.0.24.12.12",
    'license': "LGPL-3",
    'depends': ['base', 'product', 'contacts', 'account', 'woo_product_connector'],
    'data': [
        # Views
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
    ],
}
