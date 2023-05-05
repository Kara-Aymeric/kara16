# -*- coding: utf-8 -*-
{
    'name': 'Commission sur les ventes',
    'version': '16.0.23.01.20',
    'category': 'Sales/Sales',
    'summary': 'Ce module permet de générer des commissions par lignes de vente en fonction de l\'article choisi.',
    'description': """
        Ce module permet de générer des commissions pr ligne de vente en fonction de l\'article choisi. 
        Le type ainsi que le montant est paramétrable au niveau de l'article.
        Une facture regroupant les commissions peut être générée.
    """,
    'website': 'https://hennet-solutions.fr',
    'license': 'LGPL-3',
    'depends': ['account', 'sale'],
    'data': [
        # Data
        'data/product_data.xml',

        # Report
        'report/sale_report_templates.xml',

        # Security
        'security/ir.model.access.csv',

        # Views
        'views/account_tax_views.xml',
        'views/product_template_views.xml',
        'views/res_company_views.xml',
        'views/sale_order_views.xml',
        'views/sale_commission_menus.xml',
    ],
}
