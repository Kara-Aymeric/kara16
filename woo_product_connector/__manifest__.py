# -*- coding: utf-8 -*-
{
    'name': 'Woo product connector',
    'version': '16.0.23.05.11',
    'category': 'Sales/Sales',
    'summary': """Facilite la connexion concernant les fiches produits entre WooCommerce et Odoo pour Agorane""",
    'description': """Facilite la connexion concernant les fiches produits entre WooCommerce et Odoo pour Agorane""",
    'website': 'https://hennet-solutions.fr',
    'license': 'LGPL-3',
    'depends': ['sale'],
    'data': [
        # Security
        'security/ir.model.access.csv',
        # Views
        'views/product_template_views.xml',
        'views/product_views.xml',
        'views/woo_product_connector_menus.xml',
    ],
}
