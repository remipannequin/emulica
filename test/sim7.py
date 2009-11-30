#! /usr/bin/python
# *-* coding: utf8 *-*

import sys
sys.path.insert(0, "../src/")
from emulica.emulation import *
from emulica.properties import SetupMatrix

exp_result_product = [(1, [(3, 7, 'machine', 'p1')], 
                          [(0, 'source'), 
                           (0, 'transporter'), 
                           (2, 'espaceMachine'), 
                           (7, 'transporter'), 
                           (10, 'sink')], 0, 80), 
                      (2, [(14, 22, 'machine', 'p3')], 
                          [(0, 'source'),
                           (10, 'transporter'), 
                           (12, 'espaceMachine'), 
                           (22, 'transporter'), 
                           (25, 'sink')], 0, 80), 
                      (3, [(28, 35, 'machine', 'p2')],
                          [(0, 'source'), 
                           (25, 'transporter'), 
                           (27, 'espaceMachine'), 
                           (35, 'transporter'), 
                           (38, 'sink')], 0, 80), 
                      (4, [(40, 45, 'machine', 'p2')], 
                          [(0, 'source'), 
                           (38, 'transporter'), 
                           (40, 'espaceMachine'), 
                           (45, 'transporter'), 
                           (48, 'sink')], 0, 80), 
                      (5, [(52, 56, 'machine', 'p1')], 
                          [(0, 'source'), 
                           (48, 'transporter'), 
                           (50, 'espaceMachine'), 
                           (56, 'transporter'), 
                           (59, 'sink')], 0, 80), 
                      (6, [(63, 71, 'machine', 'p3')], 
                          [(0, 'source'), 
                           (59, 'transporter'), 
                           (61, 'espaceMachine'), 
                           (71, 'transporter'), 
                           (74, 'sink')], 0, 80)] 
exp_result_resource = [[(0, 0, 'setup'), 
                        (0, 2, 'load'), 
                        (7, 7, 'setup'), 
                        (7, 10, 'unload'), 
                        (10, 10, 'setup'), 
                        (10, 12, 'load'), 
                        (22, 22, 'setup'), 
                        (22, 25, 'unload'), 
                        (25, 25, 'setup'), 
                        (25, 27, 'load'), 
                        (35, 35, 'setup'), 
                        (35, 38, 'unload'), 
                        (38, 38, 'setup'), 
                        (38, 40, 'load'), 
                        (45, 45, 'setup'), 
                        (45, 48, 'unload'), 
                        (48, 48, 'setup'), 
                        (48, 50, 'load'), 
                        (56, 56, 'setup'), 
                        (56, 59, 'unload'), 
                        (59, 59, 'setup'), 
                        (59, 61, 'load'), 
                        (71, 71, 'setup'), 
                        (71, 74, 'unload')], 
                       [(2, 3, 'setup'), 
                        (3, 7, 'p1'), 
                        (12, 14, 'setup'), 
                        (15, 17, 'failure'), 
                        (14, 22, 'p3'), 
                        (27, 28, 'setup'), 
                        (32, 34, 'failure'), 
                        (28, 35, 'p2'), 
                        (40, 40, 'setup'), 
                        (40, 45, 'p2'), 
                        (49, 51, 'failure'), 
                        (51, 52, 'setup'), 
                        (52, 56, 'p1'), 
                        (61, 63, 'setup'), 
                        (66, 68, 'failure'), 
                        (63, 71, 'p3')]]


class ControlCreate(Process):
    def run(self, model):
        n = 0
        i = 0
        create = model.modules["create"]
        pType = ['type1', 'type2', 'type3', 'type3']
        while n < 6:
            m = Request("create", "create",params={'productType':pType[i]})
            yield put, self, create.request_socket, [m]
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
    sp.add_program('unload', 3, {'source':espaceMachine, 'destination':sink})
    machine = ShapeAct(model, "machine", espaceMachine)
    machine.add_program('p1', 4)
    machine.add_program('p2', 5)
    machine.add_program('p3', 6)
    m = SetupMatrix(machine.properties,1)
    m.add('p1','p3',2)
    m.add('p3','p1',3)
    machine['setup'] = m
    fail1 = Failure(model, "fail1", 15, 2, [machine])
    
    initialize_control(model)
    return model

def initialize_control(model):
    model.register_control(ControlCreate)
    model.register_control(ControlMachine)
    
def start(model):
    model.emulate(until=80)

def step(model, tempo):
    model.emulate(tempo = tempo, until=80)

if __name__ == '__main__':
    model = create_model()
    start(model)
    add_trace('T',model.modules["transporter"].trace)
    add_trace('M', model.modules["machine"].trace)
    plot('svg', '-')
