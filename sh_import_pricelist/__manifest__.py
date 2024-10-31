# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Import Pricelist",
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "version": "16.0.2",
    "category": "Extra Tools",
    "summary": "Import Sales Pricelist Import Vendor Pricelist Import Price List Import Pricelist from Excel Import Pricelist from CSV Import Bulk Pricelist Import Pricelist XLS pricelist from XLSX import multiple pricelist lines import product pricelists Odoo",
    "description": """Currently, odoo does not provide any kind of feature for import different sales and vendor pricelists. Using this module you can import different sales pricelists and vendor pricelists from CSV/Excel file. You can apply a pricelist by name, internal reference number & barcode.""",
    "depends": [
        'sale_management',
        'purchase',
        'sh_message',
    ],
    "data": [
        "security/import_pricelist_security.xml",
        "security/ir.model.access.csv",
        'wizard/product.xml',
        "wizard/import_sale_pricelist_wizard_views.xml",
        "wizard/import_vendor_pricelist_wizard_views.xml",
    ],
    "images": ["static/description/background.png", ],
    "license": "OPL-1",
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": "37",
    "currency": "EUR"
}
