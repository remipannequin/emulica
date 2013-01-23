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
In this model, we test if the same report socket can be created and attached to several modules.
"""


import sys
import os.path
import unittest
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

import emulica.emulation as emu

EXP_REPORT_LIST = [emu.Report("create1", "create-done", date = d*10) for d in range(11)]
EXP_REPORT_LIST.insert(1, emu.Report("observer1", "ev1", location = "holder1", date = 0))
report_list = []

EMULATE_UNTIL = 100;


class ControlCreate(emu.Process):
    def run(self, model):
        n = 0
        createModule = model.modules["create1"]
        while n < 10:
            m = emu.Request("create1", "create")
            yield emu.put, self, createModule.request_socket, [m]
            yield emu.hold, self, 10

class ReportMonitor(emu.Process):
    def run(self, model):
        """PEM : create a Store, and attach it to every module in the model"""
        queue = emu.Store()
        for module in model.modules.values():
            module.attach_report_socket(queue)
        while True:
            yield emu.get, self, queue, 1
            report = self.got[0]
            report_list.append(report)

def get_model():
    model = emu.Model()
    h = emu.Holder(model, "holder1")
    obs1 = emu.PushObserver(model, "observer1", "ev1", observe_type = False, holder = h)
    c = emu.CreateAct(model, "create1", h)
    #control processes
    model.register_control(ControlCreate)
    model.register_control(ReportMonitor)
    return model





class TestSim13(unittest.TestCase):
    
    def test_ModelCreate(self):
        get_model()

    def test_Start(self):
        model = get_model()
        model.emulate(until = EMULATE_UNTIL)

    def test_RunResults(self):
        model = get_model()
        model.emulate(until = EMULATE_UNTIL)
        self.assertEqual(report_list, EXP_REPORT_LIST)

if __name__ == '__main__':    
    unittest.main()

