# -*- coding: utf-8 -*-
{
    'name': 'OMS routing orders',
    'version': '16.0.23.02.20',
    'category': 'Sales/CRM',
    'summary': """oms routing wms orders""",
    'description': """mamanage rules for routing orders in approiate warehouse""",
    'website': 'https://irokoo.fr',
    'license': 'LGPL-3',
    'depends': ['sale_management', 'stock', 'sale_stock'],
    'data': [
            'views/stock_warehouse_view.xml',
            ],
}
