# -*- coding: utf-8 -*-
{
    'name': "CRM personnalisé",
    'summary': """Personnalisation du module CRM pour Agorane""",
    'description': """Personnalisation du module CRM pour Agorane""",
    'author': "Kévin HENNION",
    'website': "https://hennet-solutions.fr",
    'category': 'Sales/CRM',
    'version': '16.0.24.11.06',
    'license': "LGPL-3",
    'installable': True,
    'depends': ['base', 'contacts', 'crm', 'product', 'account', 'sale'],
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Views
        'views/account_move_views.xml',
        'views/crm_lead_views.xml',
        'views/partner_typology_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
    ],
}
