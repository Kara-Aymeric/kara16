# -*- coding: utf-8 -*-

from . import models
from . import spacefillpy

def pre_init_hook(cr):
    from odoo.service import common
    from odoo.exceptions import Warning
    version_info = common.exp_version()
    server_serie = version_info.get('server_serie')
    #if server_serie != '15.0':
    #    raise Warning(
    #        'Module support Odoo series 15.0, found {}.'.format(server_serie))
    return True

def post_init_hook(cr, registry):
    from odoo import api, SUPERUSER_ID
    from odoo.tools import convert_file
    convert_file(cr, 'stock_spacefill', 'data/spacefill.statut.csv', None, mode='init', noupdate=True, kind='init')