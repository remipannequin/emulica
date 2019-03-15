#!/usr/bin/python
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2013 Rémi Pannequin, Centre de Recherche en Automatique de Nancy remi.pannequin@univ-lorraine.fr
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE


"""
Test exceptions in core.emulation
"""



import unittest

import util
util.set_path()

import logging
from emulica.core import set_up_logging
set_up_logging(logging.WARNING)

from emulica.core import emulation
import logging
logger = logging.getLogger('test_exceptions')


class InsertRequest:
    def run(self, model, rq):
        yield model.get_sim().timeout(1)
        model.insert_request(rq)
        yield model.get_sim().timeout(10)

class TestException(unittest.TestCase):
    def setUp(self):
        print(self.id())
        
    def test_create(self):
        model = emulation.Model()
        h = emulation.Holder(model, "h")
        create = emulation.CreateAct(model, "c")
        #rq = emulation.Request("c", 'create')
        #odel.register_control(InsertRequest, pem_args=(model, rq))
        
        self.assertRaises(emulation.EmulicaError, model.emulate,10)

    def test_dispose(self):
        model = emulation.Model()
        h = emulation.Holder(model, "h")
        dispose = emulation.DisposeAct(model, "d")
        #rq = emulation.Request("d", 'create')
        #model.register_control(InsertRequest, pem_args=(model, rq))
        self.assertRaises(emulation.EmulicaError, model.emulate,10)
        
        
        
        

if __name__ == '__main__':    
    unittest.main()
