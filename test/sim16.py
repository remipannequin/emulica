#! /usr/bin/python
# *-* coding: utf8 *-*
"""Submodel testing: use a model property in the control system"""


import sys
sys.path.insert(0, "../src/")
from emulica.emulation import *

exp_result_product = [(1, [(3, 7, 'cell.machine', 'p1')], [(0, 'cell.source'),
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
                      
exp_result_resource = [[(0, 0, 'setup'),
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
            print "waiting %s" % model['delay']
            yield hold, self, model['delay']
             

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
    machine.add_program('p1', 4)
    machine.add_program('p2', 5)
    machine.add_program('p3', 6)
    m = SetupMatrix(1)
    m.add('p1','p3',2)
    m.add('p3','p1',3)
    machine['setup'] = m
    initialize_control_submodel(model)
    model.add_property('delay', 'INT', delay)
    
    
    
def initialize_control_submodel(model):
    model.register_control(ControlCell)

def create_model():
    model = Model()
    create_submodel(model, "cell", 10)
    source = model.get_module("cell.source")
    CreateAct(model, "create", source)
    sink = model.get_module("cell.sink")
    DisposeAct(model, "dispose", sink)
    PushObserver(model, "obsSink", "sink-ready", holder = sink)
    
    initialize_control(model)
    return model

def initialize_control(model):
    model.register_control(ControlCreate)
    model.register_control(ControlDispose)


def start(model):
    model.emulate(until=50)

if __name__ == '__main__':
    model = create_model()
    start(model)
    result_product = [(pid, p.shape_history, 
                       p.space_history, 
                       p.create_time, 
                       p.dispose_time) for (pid, p) in model.products.items()]
    result_resource = [model.get_module("cell.transporter").trace, model.get_module("cell.machine").trace]
    print result_product
    print result_resource
