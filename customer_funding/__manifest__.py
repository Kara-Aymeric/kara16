# -*- coding: utf-8 -*-
{
    'name': 'Financement',
    'version': '16.0.24.06.12',
    'category': 'Sales/Sales',
    'summary': """Gestion des financements clients""",
    'description': """Gestion des financements clients""",
    'website': 'https://hennet-solutions.fr',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'contacts',
        'sale'
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Views
        'views/account_payment_term_views.xml',
        'views/res_partner_views.xml',
        'views/partner_financier_views.xml',
        'views/sale_order_views.xml',
    ],
}
