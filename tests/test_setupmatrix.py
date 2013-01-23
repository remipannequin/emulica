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

from emulica.properties import SetupMatrix, Registry
from emulica import emulation



class TestSetupmatrix(unittest.TestCase):
    
    def test_setUp(self):
        model = emulation.Model()
        p = emulation.Product(model)
        self.m = SetupMatrix(Registry(p, model.rng), 3)

    def compare(self, init, final, expRes):
        t = self.m.get(init, final)
        self.assertEqual(t, expRes)



    def test_AddValues(self):
        self.m.add('p1', 'p2', 1)
        v = test('p1', 'p2', 1)
        self.m.add('p1', 'p3', 2)
        self.compare('p1', 'p3', 2)
        self.compare('p0', 'p0', 0)
        self.compare('p0', 'p1', 3)
        self.m.add('p2', 'p3', 4)
        self.compare('p2', 'p3', 4)
        self.compare('p1', 'p2', 1)
        self.compare('p1', 'p3', 2)
        self.m.add('p3', 'p1', 5)
        self.compare('p3', 'p1', 5)


    def test_ModValue(self):
        self.m = SetupMatrix(Registry(p, model.rng), 3)
        self.m.add('p3', 'p1', 5)
        self.m.modify('p3', 'p1', new_final = 'p12')
        self.compare('p3', 'p12', 5)
        self.m.add('p2', 'p3', 4)
        self.m.modify('p2', 'p3', new_initial = 'p12')
        self.compare('p12', 'p3', 4)
        self.m.add('p1', 'p2', 1)
        self.m.modify('p1', 'p2', new_time = 2)
        self.compare('p1', 'p2', 2)
        
        
if __name__ == '__main__':    
    unittest.main()
        
        
