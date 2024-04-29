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
        'base',
        'account',
    ],
    'data': [
        # Data
        'data/ir_cron_data.xml',
        'data/mail_template_data.xml',
        'data/payment_reminder_data.xml',

        # Security
        'security/ir.model.access.csv',

        # Views
        'views/account_move_views.xml',
        'views/account_payment_term_views.xml',
        'views/payment_reminder_line_views.xml',
        'views/payment_reminder_views.xml',
        'views/res_company_views.xml',
        'views/res_partner_views.xml',
    ],
}
