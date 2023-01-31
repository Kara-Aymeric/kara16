# -*- coding: utf-8 -*-
#Copyright 2022 irOkoo
{
    'name': "Spacefill",
 
    'summary': """
       SpaceFill connector""",

    'description': """
        Synchronize warehouse operations with SpaceFill.
        Export and receive stock movements with SpaceFill platform.
        
    """,

    'author': "irokoo",
    'website': "https://www.spacefill.fr",
    'category': 'Inventory',
    'version': '1.0',
    'license': 'AGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base','sale_stock','delivery','purchase','sale'],

    # always loaded
    'data': [
        # DATA
        'data/ir_cron.xml',
        'data/spacefill.statut.csv',
        # SECURITY
        'security/security.xml',
        'security/ir.model.access.csv',
        # VIEWS
        'views/product_template.xml',
        'views/product_view.xml',
        'views/spacefill_statut.xml',
        'views/spacefill.xml',
        'views/spacefill_menu.xml',
        'views/stock_package_type_view.xml',
        'views/stock_warehouse_view.xml',
        'views/stock_picking_view.xml',
        'views/stock_picking_type.xml',
        ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "active": True,
    "installable": True,
    "post_init_hook": 'post_init_hook',
    "pre_init_hook" : 'pre_init_hook',   
}
