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


from emulica.emulation import *
from emulica.properties import SetupMatrix

class ControlCreate(Process):
    def run(self, model):
        n = 0
        i = 0
        pType = ['type1', 'type2', 'type3']
        createModule = model.get_module("create")
        while n < 4:
            m = Request("create", "create",params={'productType':pType[i]})
            yield put, self, createModule.request_socket, [m]
            i = (i+1)%3
            n += 1

class ControlDispose(Process):
    def run(self, model):
        dispose = model.get_module('dispose')
        obs = model.get_module('obsSink')
        rp_obs = obs.create_report_socket()
        while True:
            yield get, self, rp_obs, 1
            yield put, self, dispose.request_socket, [Request("dispose", "dispose")]

class ControlCell(Process):
    def run(self, model):
        prog = {'type1':'p1','type2':'p3','type3':'p2'}
        sp = model.get_module("transporter")
        machine = model.get_module("machine")
        rp_machine = machine.create_report_socket()
        obs1 = model.get_module("obsSource")
        rp_obs1 = obs1.create_report_socket()
        obs2 = model.get_module("obsMachine")
        rp_obs2 = obs2.create_report_socket()
        while True:
            ##attente de l'arrivée d'un pièce
            yield get, self, rp_obs1, 1
            ev = self.got[0]
            rq = Request("transporter","move",params={'program':'load'})
            yield put, self, sp.request_socket, [rq]
            ##pièce prête
            yield get, self, rp_obs2, 1
            ev = self.got[0]
            p = prog[ev.how['productType']]
            yield put, self, machine.request_socket, [Request("machine","setup", params={"program":p})]
            ##début process
            yield put, self, machine.request_socket, [Request("machine","make")]
            ##attente fin process
            fin = False
            while not fin:
                yield get, self, rp_machine, 1
                fin = self.got[0].what=="idle"
            ##déchargement
            yield put, self, sp.request_socket, [Request("transporter", "move", params={"program":'unload'})]

def get_model():
    model = Model()
    
    submodel = Model(model = model, name = "cell", path = 'cell.emu')
    source = Holder(submodel, "source")
    sink = Holder(submodel, "sink")
    espaceMachine = Holder(submodel, "espaceMachine")
    PushObserver(submodel, "obsSource", "source-ready", observe_type = False, holder = source)
    PushObserver(submodel, "obsMachine", "machine-ready", holder = espaceMachine)
    sp = SpaceAct(submodel, "transporter")
    sp.add_program('load', 2, {'source':source, 'destination':espaceMachine})
    sp.add_program('unload', 2, {'source':espaceMachine, 'destination':sink})
    machine = ShapeAct(submodel, "machine", espaceMachine)
    machine.add_program('p1', 4)
    machine.add_program('p2', 5)
    machine.add_program('p3', 6)
    m = SetupMatrix(machine.properties, 1)
    m.add('p1','p3',2)
    m.add('p3','p1',3)
    machine['setup'] = m
    submodel.register_control(ControlCell)
    
    source = model.get_module("cell.source")
    CreateAct(model, "create", source)
    sink = model.get_module("cell.sink")
    DisposeAct(model, "dispose", sink)
    PushObserver(model, "obsSink", "sink-ready", holder = sink)
    model.register_control(ControlCreate)
    model.register_control(ControlDispose)
    return model

def register_control(model):
    model.register_control(ControlCreate)
    model.register_control(ControlDispose)
    return model

class TestSim15(unittest.TestCase):
    """
    In this very simple example, we create the mot simple model possible:
    a create actuator put some product in a holder. These product trigger 
    a dispose actuator thanks to a product observer on the holder.
    """
    
    def setUp(self): 
        self.exp_result_product = [(1, [(3, 7, 'cell.machine', 'p1')], 
                          [(0, 'cell.source'), 
                           (0, 'cell.transporter'), 
                           (2, 'cell.espaceMachine'), 
                           (7, 'cell.transporter'), 
                           (9, 'cell.sink')], 0, 9), 
                      (2, [(13, 19,'cell.machine', 'p3')], 
                          [(0, 'cell.source'),
                           (9, 'cell.transporter'), 
                           (11, 'cell.espaceMachine'), 
                           (19, 'cell.transporter'), 
                           (21, 'cell.sink')], 0, 21), 
                      (3, [(24, 29, 'cell.machine', 'p2')],
                          [(0, 'cell.source'),
                           (21, 'cell.transporter'), 
                           (23, 'cell.espaceMachine'), 
                           (29, 'cell.transporter'), 
                           (31, 'cell.sink')], 0, 31), 
                      (4, [(34, 38, 'cell.machine', 'p1')],
                          [(0, 'cell.source'),
                           (31, 'cell.transporter'), 
                           (33, 'cell.espaceMachine'), 
                           (38, 'cell.transporter'), 
                           (40, 'cell.sink')], 0, 40)] 
                      
        self.exp_result_resource = [[(0, 0, 'setup'), 
                        (0, 2, 'load'), 
                        (7, 7, 'setup'), 
                        (7, 9, 'unload'), 
                        (9, 9, 'setup'), 
                        (9, 11, 'load'), 
                        (19, 19, 'setup'), 
                        (19, 21, 'unload'), 
                        (21, 21, 'setup'), 
                        (21, 23, 'load'), 
                        (29, 29, 'setup'), 
                        (29, 31, 'unload'), 
                        (31, 31, 'setup'), 
                        (31, 33, 'load'), 
                        (38, 38, 'setup'), 
                        (38, 40, 'unload')], 
                       [(2, 3, 'setup'), 
                        (3, 7, 'p1'), 
                        (11, 13, 'setup'), 
                        (13, 19, 'p3'), 
                        (23, 24, 'setup'), 
                        (24, 29, 'p2'), 
                        (33, 34, 'setup'), 
                        (34, 38, 'p1')]]
    
    

        
    def test_ModelCreate(self):
        get_model()

    def test_Start(self):
        model = get_model()
        model.emulate(until = 50)

    def test_RunResults(self):
        model = get_model()
        model.emulate(until = 50)
        result_product = [(pid, p.shape_history, 
                       p.space_history, 
                       p.create_time, 
                       p.dispose_time) for (pid, p) in model.products.items()]
        result_resource = [model.get_module("cell.transporter").trace, model.get_module("cell.machine").trace]
        self.assertEqual(result_product, self.exp_result_product)
        self.assertEqual(result_resource, self.exp_result_resource)


if __name__ == '__main__':    
    unittest.main()

