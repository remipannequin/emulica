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

import sys
import os.path
import unittest
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from emulica import controler
import test_sim12

class TestServer(unittest.TestCase):
    
    def setUp(self):
        self.model = test_sim12.get_model()
        
        "<request><who>emulator</who><what>start</what></request>"
    
    def todotest_Create(self):
        serv = controler.EmulationServer(self.model, 51000)
        
    def todotest_Start(self):
        serv = controler.EmulationServer(self.model, 51001)
        serv.start()
        #temporisation ?
        result = [(pid, 
                   p.shape_history, 
                   p.space_history, 
                   p.create_time, 
                   p.dispose_time) for (pid, p) in self.model.products.items()]
        self.assertEqual(result, EXP_RESULT)
        
if __name__ == '__main__':    
    unittest.main()
        
