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

EXP_RESULT = [(1, [], [(0. , 'holder1')], 0., 3.5),
              (2, [], [(2., 'holder1')], 2., 5.5), 
              (3, [], [(4., 'holder1')], 4., 7.0), 
              (4, [], [(5., 'holder1')], 5., 8.5), 
              (5, [], [(6., 'holder1')], 6., 10.), 
              (6, [], [(7., 'holder1')], 7., 11.5),
              (7, [], [(7.5, 'holder1')], 7.5, 13.),
              (8, [], [(8., 'holder1')], 8., 14.5)]
              
              
EXP_RESULT_POSITION =  [(0.5, {4.0: 1}), 
                        (1.0, {3.0: 1}), 
                        (1.5, {2.0: 1}), 
                        (2, {1.0: 1, 5: 2}), 
                        (2.5, {0: 1, 4.0: 2}), 
                        (3.0, {0: 1, 3.0: 2}), 
                        (3.5, {2.0: 2}), 
                        (4.0, {1.0: 2, 4.0: 3}), 
                        (4.5, {0: 2, 3.0: 3}), 
                        (5.0, {0: 2, 2.0: 3, 4.0: 4}), 
                        (5.5, {1.0: 3, 3.0: 4}), 
                        (6.0, {0: 3, 2.0: 4, 4.0: 5}), 
                        (6.5, {0: 3, 1: 4, 3.0: 5}), 
                        (7.0, {1.0: 4, 2.0: 5, 4.0: 6}), 
                        (7.5, {0: 4, 1: 5, 3.0: 6, 4.0: 7}), 
                        (8.0, {0: 4, 1: 5, 2: 6, 3: 7, 4: 8}), 
                        (8.5, {1.0: 5, 2.0: 6, 3.0: 7, 4.0: 8}), 
                        (9.0, {0: 5, 1: 6, 2: 7, 3: 8}), 
                        (9.5, {0: 5, 1: 6, 2: 7, 3: 8}), 
                        (10.0, {1.0: 6, 2.0: 7, 3.0: 8}), 
                        (10.5, {0: 6, 1: 7, 2: 8}), 
                        (11.0, {0: 6, 1: 7, 2: 8}), 
                        (11.5, {1.0: 7, 2.0: 8}), 
                        (12.0, {0: 7, 1: 8}), 
                        (12.5, {0: 7, 1: 8}), 
                        (13.0, {1.0: 8}), 
                        (13.5, {0: 8}), 
                        (14.0, {0: 8}), 
                        (14.5, {}), 
                        (15.0, {}), 
                        (15.5, {}), 
                        (16.0, {})]

pos_list = list()

EMULATE_UNTIL = 16;

class ControlCreate(emu.Process):
    def run(self, model):
        createModule = model.modules["create1"]
        requests = [emu.Request("create1", "create", date = t) for t in [0., 2., 4., 5., 6., 7., 7.5, 8.]]
        yield emu.put, self, createModule.request_socket, requests
                    

class ControlDispose(emu.Process):
    def run(self, model):
        disposeModule = model.modules["dispose1"]
        observerModule = model.modules["observer1"]
        report = observerModule.create_report_socket()
        while True:
            yield emu.get, self, report, 1
            yield emu.put, self, disposeModule.request_socket, [emu.Request("dispose1","dispose", date = emu.now()+1)]

class ObsMonitor(emu.Process):
    def run(self, model):
        obs = model.modules["observer2"]
        report = obs.create_report_socket()
        while True:
            yield emu.put, self, obs.request_socket, [emu.Request("observer2","observe", date = emu.now() + 0.5)]
            yield emu.get, self, report, 1
            r = self.got[0]
            pos_list.append((r.when, r.how['ID_by_position']))
            
            
def get_model(stepping = False):
    pos_list = list()
    model = emu.Model()
    h = emu.Holder(model, "holder1")
    h['capacity'] = 5
    h['speed'] = 2
    obs1 = emu.PushObserver(model, "observer1", "ev1", observe_type = False, holder = h)
    obs2 = emu.PullObserver(model, "observer2", "position", holder = h)
    c = emu.CreateAct(model, "create1", h)
    d = emu.DisposeAct(model, "dispose1", h)
    model.register_control(ControlDispose)
    model.register_control(ControlCreate)
    model.register_control(ObsMonitor)
    return model

def register_control(model):
    model.register_control(ControlDispose)
    model.register_control(ControlCreate)
    model.register_control(ObsMonitor)
    return model


class TestSim8(unittest.TestCase):
        
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
        self.assertEqual(pos_list, EXP_RESULT_POSITION)


if __name__ == '__main__':    
    unittest.main()

