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

"""Submodel: model properties: linking model properties and module parameters."""

import sys
import os.path
import unittest
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from emulica.emulation import *
from emulica.properties import SetupMatrix, ProgramTable

EXP_RESULT_PRODUCT = [(1, [(3, 7, 'cell.machine', 'p1')], [(0, 'cell.source'),
                                                           (0, 'cell.transporter'),
                                                           (2, 'cell.espaceMachine'),
                                                           (7, 'cell.transporter'),
                                                           (9, 'cell.sink')], 0, 9),
                      (2, [(21, 27, 'cell.machine', 'p3')], [(0, 'cell.source'),
                                                             (17, 'cell.transporter'),
                                                             (19, 'cell.espaceMachine'),
                                                             (27, 'cell.transporter'),
                                                             (29, 'cell.sink')], 0, 29),
                      (3, [(40, 45, 'cell.machine', 'p2')], [(0, 'cell.source'),
                                                             (37, 'cell.transporter'),
                                                             (39, 'cell.espaceMachine'),
                                                             (45, 'cell.transporter'),
                                                             (47, 'cell.sink')], 0, 47),
                      (4, [], [(0, 'cell.source')], 0, 50)]
                      
EXP_RESULT_RESOURCE = [[(0, 0, 'setup'),
                        (0, 2, 'load'),
                        (7, 7, 'setup'),
                        (7, 9, 'unload'),
                        (17, 17, 'setup'),
                        (17, 19, 'load'),
                        (27, 27, 'setup'),
                        (27, 29, 'unload'),
                        (37, 37, 'setup'),
                        (37, 39, 'load'),
                        (45, 45, 'setup'),
                        (45, 47, 'unload')],
                       [(2, 3, 'setup'),
                        (3, 7, 'p1'),
                        (19, 21, 'setup'),
                        (21, 27, 'p3'),
                        (39, 40, 'setup'),
                        (40, 45, 'p2')]]

EMULATE_UNTIL = 50

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
            print "delay = %s" % machine['program_table'][p].time()
            ##début process
            yield put, self, machine.request_socket, [Request("machine","make")]
            ##attente fin process
            fin = False
            while not fin:
                yield get, self, rp_machine, 1
                fin = self.got[0].what=="idle"
            ##déchargement
            yield put, self, sp.request_socket, [Request("transporter", "move", params={"program":'unload'})]
            
             

def create_submodel(parent, name, delay):
    model = Model(model = parent, name = name, path = 'cell.gseme')
    source = Holder(model, "source")
    sink = Holder(model, "sink")
    espaceMachine = Holder(model, "espaceMachine")
    PushObserver(model, "obsSource", "source-ready", observe_type = False, holder = source)
    PushObserver(model, "obsMachine", "machine-ready", holder = espaceMachine)
    sp = SpaceAct(model, "transporter")
    sp.add_program('load', 2, {'source':source, 'destination':espaceMachine})
    sp.add_program('unload', 2, {'source':espaceMachine, 'destination':sink})
    machine = ShapeAct(model, "machine", espaceMachine)
    model.inputs['p_table'] = ("machine", 'program_table')
    model.apply_inputs()
    #machine.properties['program_table'] = "model['p_table']"
    #machine.properties.set_auto_eval('program_table')
    m = SetupMatrix(machine.properties, 1)
    m.add('p1','p3',2)
    m.add('p3','p1',3)
    machine['setup'] = m
    initialize_control_submodel(model)
    def set_delay(value):
        machine['program_table']['p2']
    model.properties.add_with_display('delay', 'FLOAT', delay, "Delay")
    p_table = model['p_table']
    p_table.add_program('p1', 6)
    p_table.add_program('p2', 7)
    p_table.add_program('p3', 8)
    return model
    
def initialize_control_submodel(model):
    model.register_control(ControlCell)

def get_model():
    model = Model()
    submodel = create_submodel(model, "cell", 10)
    submodel['delay'] = 7
    source = model.get_module("cell.source")
    CreateAct(model, "create", source)
    sink = model.get_module("cell.sink")
    DisposeAct(model, "dispose", sink)
    PushObserver(model, "obsSink", "sink-ready", holder = sink)
    model.register_control(ControlCreate)
    model.register_control(ControlDispose)
    return model

def initialize_control(model):
    model.register_control(ControlCreate)
    model.register_control(ControlDispose)



class TestSim17(unittest.TestCase):
        
    def test_ModelCreate(self):
        get_model()

    def test_Start(self):
        model = get_model()
        model.emulate(until = EMULATE_UNTIL)

    def test_RunResults(self):
        model = get_model()
        model.emulate(until = EMULATE_UNTIL)
        result_product = [(pid, 
                       p.shape_history, 
                       p.space_history,
                       p.create_time, 
                       p.dispose_time) for (pid, p) in model.products.items()]
        result_resource = [model.get_module("cell.transporter").trace, model.get_module("cell.machine").trace]
        self.assertEqual(result_product, EXP_RESULT_PRODUCT)
        self.assertEqual(result_resource, EXP_RESULT_RESOURCE)


if __name__ == '__main__':    
    unittest.main()

