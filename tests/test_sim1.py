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

import emulica.emulation as emu

EXP_RESULT = [(1, [], [(0, 'holder1')], 0, 4),
              (2, [], [(10, 'holder1')], 10, 14), 
              (3, [], [(20, 'holder1')], 20, 24), 
              (4, [], [(30, 'holder1')], 30, 34), 
              (5, [], [(40, 'holder1')], 40, 44), 
              (6, [], [(50, 'holder1')], 50, 54), 
              (7, [], [(60, 'holder1')], 60, 64), 
              (8, [], [(70, 'holder1')], 70, 74), 
              (9, [], [(80, 'holder1')], 80, 84), 
              (10, [], [(90, 'holder1')], 90, 94), 
              (11, [], [(100, 'holder1')], 100, 100)]

EMULATE_UNTIL = 100;

#Control processes
class ControlCreate(emu.Process):
    def run(self, model):
        n = 0
        createModule = model.modules["create1"]
        report = createModule.create_report_socket()
        while n < 10:
            m = emu.Request("create1", "create")
            yield emu.put, self, createModule.request_socket, [m]
            yield emu.get, self, report, 1
            yield emu.hold, self, 10

class ControlDispose(emu.Process):
    def run(self, model):
        disposeModule = model.modules["dispose1"]
        observerModule = model.modules["observer1"]
        report = observerModule.create_report_socket()
        while True:
            yield emu.get, self, report, 1
            yield emu.put, self, disposeModule.request_socket, [emu.Request("dispose1","dispose",date=emu.now()+4)]
        

def get_model():
    model = emu.Model()
    h = emu.Holder(model, "holder1")
    obs1 = emu.PushObserver(model, "observer1", "ev1", observe_type = False, holder = h)
    c = emu.CreateAct(model, "create1", h)
    d = emu.DisposeAct(model, "dispose1", h)
    model.register_control(ControlCreate)
    model.register_control(ControlDispose)
    return model

def register_control(model):
    model.register_control(ControlCreate)
    model.register_control(ControlDispose)
    return model

class TestSim1(unittest.TestCase):
    """
    In this very simple example, we create the mot simple model possible:
    a create actuator put some product in a holder. These product trigger 
    a dispose actuator thanks to a product observer on the holder.
    """

    def test_ModelCreate(self):
        get_model()

    def test_ModelControl(self):
        #register control processes
        model = emu.Model()
        model.register_control(ControlCreate)
        model.register_control(ControlDispose)

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

    def test_MultipleRun(self):
        model = get_model()
        model.emulate(until = EMULATE_UNTIL)
        model.emulate(until = EMULATE_UNTIL)
        result = [(pid, 
                   p.shape_history, 
                   p.space_history, 
                   p.create_time, 
                   p.dispose_time) for (pid, p) in model.products.items()]
        self.assertEqual(result, EXP_RESULT)


if __name__ == '__main__':    
    unittest.main()

