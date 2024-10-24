# -*- coding: utf-8 -*-
{
    'name': 'Salespeople disable filter',
    'version': '16.0.24.10.24',
    'category': 'Sales/Sales',
    'summary': 'Ce module permet de supprimer le domaine de filtre par défaut sur les vendeurs.',
    'description': """
        Ce module permet de supprimer le domaine de filtre par défaut sur les vendeurs (Contacts, CRM, Ventes, Factures).
    """,
    'website': 'https://hennet-solutions.fr',
    'license': 'LGPL-3',
    'depends': ['base', 'crm', 'account', 'sale'],
    'data': [
        # Views
        'views/account_move_views.xml',
        'views/crm_lead_views.xml',
        'views/res_partner_views.xml',
    ],
}
