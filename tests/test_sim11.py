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
This simple model based on sim1 tests the insert_request() method of emulation.Model
"""


import sys
import os.path
import unittest
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

import emulica.emulation as emu

EXP_RESULT = [(1, [], [(5, 'holder1')], 5, 30),
              (2, [], [(15, 'holder1')], 15, 30),
              (3, [], [(30, 'holder1')], 30, 30)]

EMULATE_UNTIL = 100;

class ControlCreate(emu.Process):
    def run(self, model):
        rq = emu.Request("create1", "create")
        yield emu.hold, self, 5
        model.insert_request(rq)
        yield emu.hold, self, 10
        model.insert_request(rq)
        yield emu.hold, self, 15
        model.insert_request(rq)
        
def get_model():
    model = emu.Model()
    h = emu.Holder(model, "holder1")
    c = emu.CreateAct(model, "create1", h)
    model.register_control(ControlCreate)
    return model
    
    
class TestSim11(unittest.TestCase):
        
    def test_ModelCreate(self):
        get_model()

    def test_Start(self):
        model = get_model()
        model.emulate(until = EMULATE_UNTIL)

    def test_RunResults(self):
        model = get_model()
        model.emulate(until = EMULATE_UNTIL)
        result = [(pid, 
               p.shape_history, 
               p.space_history, 
               p.create_time, 
               p.dispose_time) for (pid, p) in model.products.items()]
        self.assertEqual(result, EXP_RESULT)


if __name__ == '__main__':    
    unittest.main()

