# -*- coding: utf-8 -*-
{
    'name': "Relance de paiement personnalisé",
    'summary': """Personnalisation des relances de paiements pour Agorane""",
    'description': """Personnalisation des relances de paiements pour Agorane""",
    'author': "Kévin HENNION",
    'website': "https://hennet-solutions.fr",
    'category': 'Accounting/Accounting',
    'version': '16.0.24.04.10',
    'license': "LGPL-3",
    'installable': True,
    "depends": [
        'account',
    ],
    'data': [
        # Views
        'views/account_payment_term_views.xml',
        'views/res_partner_views.xml',
    ],
}
