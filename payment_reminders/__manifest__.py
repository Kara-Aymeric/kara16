# -*- coding: utf-8 -*-
# © 2018-Today Aktiv Software (http://www.aktivsoftware.com).
# Part of AktivSoftware See LICENSE file for full copyright
# and licensing details.

# Author: Aktiv Software PVT. LTD.
# mail:   odoo@aktivsoftware.com
# Copyright (C) 2015-Present Aktiv Software PVT. LTD.
# Contributions:
#           Aktiv Software:
#              -  Parth Nirmal
#              -  Dhara Solanki
#              -  Harshil soni

{
    "name": "Payment Reminders",
    "summary": """
     Send payment reminder mail on the basis of due date.
        """,
    "description": """
Send payment reminder mail on interval days before and after due
date of the invoice to respected customers.
    """,
    "author": "Aktiv Software",
    "website": "http://www.aktivsoftware.com",
    "category": "Accounting",
    "version": "16.0.1.0.0",
    "license": "OPL-1",
    "price": 18.41,
    "currency": "EUR",
    # any module necessary for this one to work correctly
    "depends": ["payment", "account_payment", "sale_management"],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "security/access_rights.xml",
        "data/mail_templates.xml",
        "data/payment_reminder_sequence.xml",
        "data/due_date_cron_views.xml",
        "views/payment_reminders_views.xml",
        "views/res_partner_views.xml",
        "views/payment_reminders_history_views.xml",
        "views/mail_template_views.xml",
        "views/res_config_setting_view.xml",
    ],
    "images": ["static/description/banner.jpg"],
    "auto_install": False,
    "installable": True,
    "application": False,
}
