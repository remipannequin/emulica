#! /usr/bin/python
# *-* coding: utf8 *-*

"""Test for the product physical charateristics. 
"""

import sys
sys.path.insert(0, "../src/")
from emulica.emulation import *
from emulica.properties import SetupMatrix

exp_result_product = [(1, [(3, 7, 'machine', 'p1')], 
                          [(0, 'source'), 
                           (0, 'transporter'), 
                           (2, 'espaceMachine'), 
                           (7, 'transporter'), 
                           (9, 'sink')],
                          {'mass': 0, 'length': 1}, 0, 34), 
                      (2, [(13, 14, 'machine', 'p3')], 
                          [(0, 'source'),
                           (9, 'transporter'), 
                           (11, 'espaceMachine'), 
                           (14, 'transporter'), 
                           (16, 'sink')],
                          {'mass': 1, 'length': 4}, 0, 34), 
                      (3, [(19, 24, 'machine', 'p2')],
                          [(0, 'source'),
                           (16, 'transporter'), 
                           (18, 'espaceMachine'), 
                           (24, 'transporter'), 
                           (26, 'sink')],
                          {'mass': 2, 'length': 3}, 0, 34), 
                      (4, [(29, 32, 'machine', 'p3')],
                          [(0, 'source'),
                           (26, 'transporter'), 
                           (28, 'espaceMachine'), 
                           (32, 'transporter'), 
                           (34, 'sink')],
                          {'mass': 3, 'length': 4}, 0, 34)] 
                                            
                      
exp_result_resource = [[(0, 0, 'setup'), 
                        (0, 2, 'load'), 
                        (7, 7, 'setup'), 
                        (7, 9, 'unload'), 
                        (9, 9, 'setup'), 
                        (9, 11, 'load'), 
                        (14, 14, 'setup'), 
                        (14, 16, 'unload'), 
                        (16, 16, 'setup'), 
                        (16, 18, 'load'), 
                        (24, 24, 'setup'), 
                        (24, 26, 'unload'), 
                        (26, 26, 'setup'), 
                        (26, 28, 'load'), 
                        (32, 32, 'setup'), 
                        (32, 34, 'unload')], 
                       [(2, 3, 'setup'), 
                        (3, 7, 'p1'), 
                        (11, 13, 'setup'), 
                        (13, 14, 'p3'), 
                        (18, 19, 'setup'), 
                        (19, 24, 'p2'), 
                        (28, 29, 'setup'), 
                        (29, 32, 'p3')]]


class ControlCreate(Process):
    def run(self, model):
        n = 0
        i = 0
        pType = ['type1', 'type2', 'type3', 'type2']
        createModule = model.modules["create"]
        while n < 4:
            m = Request("create", "create",params={'productType':pType[i], 'physical-properties': {'mass':n, 'length': 5}})
            yield put, self, createModule.request_socket, [m]
            i = (i+1)%4
            n += 1


class ControlMachine(Process):
    def run(self, model):
        prog = {'type1':'p1','type2':'p3','type3':'p2'}
        sp = model.modules["transporter"]
        machine = model.modules["machine"]
        rp_machine = machine.create_report_socket()
        obs1 = model.modules["obsSource"]
        rp_obs1 = obs1.create_report_socket()
        obs2 = model.modules["obsMachine"]
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


def create_model():
    model = Model()
    source = Holder(model, "source")
    sink = Holder(model, "sink")
    espaceMachine = Holder(model, "espaceMachine")

    obsSource = PushObserver(model, "obsSource", "source-ready", observe_type = False, holder = source)
    obsMachine = PushObserver(model, "obsMachine", "machine-ready", holder = espaceMachine)
    obsSink = PushObserver(model, "obsSink", "sink-ready", holder = sink)
    
    c = CreateAct(model, "create", source)
    sp = SpaceAct(model, "transporter")
    sp.add_program('load', 2, {'source':source, 'destination':espaceMachine})
    sp.add_program('unload', 2, {'source':espaceMachine, 'destination':sink})
    machine = ShapeAct(model, "machine", espaceMachine)
    machine.add_program('p1', 4, {'change': {'length': 1}})
    machine.add_program('p2', 5, {'change': {'length': "mass + 1"}})
    machine.add_program('p3', "product['mass']", {'change': {'length': "length - 1"}})
    m = SetupMatrix(machine.properties, 1)
    m.add('p1','p3',2)
    m.add('p3','p1',3)
    machine['setup'] = m
    initialize_control(model)
    return model

def initialize_control(model):
    model.register_control(ControlCreate)
    model.register_control(ControlMachine)

def start(model):
    model.emulate(until=50)

if __name__ == '__main__':
    model = create_model()
    start(model)
    result_product = [(pid, p.shape_history, 
                       p.space_history, 
                       p.create_time, 
                       p.dispose_time) for (pid, p) in model.products.items()]
    result_resource = [model.modules["transporter"].trace, model.modules["machine"].trace]
    print result_product
    print result_resource
