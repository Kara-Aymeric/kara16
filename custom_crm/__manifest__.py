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
    'depends': ['crm'],
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Views
        'views/crm_lead_views.xml',
    ],
}
