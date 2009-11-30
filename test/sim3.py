#! /usr/bin/python
# *-* coding: utf8 *-*
"""
source -> machine -> sink
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
                           (10, 'sink')], 0, 44),
                      (2, [(14, 20, 'machine', 'p3')], 
                          [(10, 'source'), 
                           (10, 'transporter'), 
                           (12, 'espaceMachine'), 
                           (20, 'transporter'), 
                           (23, 'sink')], 10, 44),
                      (3, [(26, 31, 'machine', 'p2')], 
                          [(20, 'source'), 
                           (23, 'transporter'), 
                           (25, 'espaceMachine'), 
                           (31, 'transporter'), 
                           (34, 'sink')], 20, 44), 
                      (4, [(37, 41, 'machine', 'p1')], 
                          [(30, 'source'), 
                           (34, 'transporter'), 
                           (36, 'espaceMachine'), 
                           (41, 'transporter'),
                           (44, 'sink')], 30, 44), 
                      (5, [], 
                          [(40, 'source'),
                           (44, 'transporter')], 40, 44)]

exp_result_resource = [[(0, 0, 'setup'), 
                        (0, 2, 'load'), 
                        (7, 7, 'setup'), 
                        (7, 10, 'unload'), 
                        (10, 10, 'setup'), 
                        (10, 12, 'load'), 
                        (20, 20, 'setup'), 
                        (20, 23, 'unload'), 
                        (23, 23, 'setup'), 
                        (23, 25, 'load'), 
                        (31, 31, 'setup'), 
                        (31, 34, 'unload'), 
                        (34, 34, 'setup'), 
                        (34, 36, 'load'),
                        (41, 41, 'setup'), 
                        (41, 44, 'unload'), 
                        (44, 44, 'setup'), 
                        (44, 44, 'load')], 
                       [(2, 3, 'setup'), 
                        (3, 7, 'p1'), 
                        (12, 14, 'setup'), 
                        (14, 20, 'p3'), 
                        (25, 26, 'setup'), 
                        (26, 31, 'p2'), 
                        (36, 37, 'setup'), 
                        (37, 41, 'p1')]]

class ControlCreate(Process):
    def run(self, model):
        n = 0
        createModule = model.modules["create"]
        report = createModule.create_report_socket()
        while n < 10:
            m = Request("create", "create")
            yield put, self, createModule.request_socket, [m]
            yield get, self, report, 1
            #print self.got[0]
            yield hold, self, 10


class ControlMachine(Process):
    def run(self, model):
        prog = ['p1','p3','p2']
        i = 0
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
            yield put, self, machine.request_socket, [Request("machine","setup", params={"program":prog[i]})]
            i = (i+ 1) % 3
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
    obsSource = PushObserver(model, "obsSource", "source-ready", holder = source)
    obsMachine = PushObserver(model, "obsMachine", "machine-ready", holder = espaceMachine)
    c = CreateAct(model, "create", source)
    sp = SpaceAct(model, "transporter")
    sp.add_program('load', 2, {'source':source, 'destination':espaceMachine})
    sp.add_program('unload', 3, {'source':espaceMachine, 'destination':sink})
    machine = ShapeAct(model, "machine", espaceMachine)
    machine.add_program('p1', 4)
    machine.add_program('p2', 5)
    machine.add_program('p3', 6)
    m = SetupMatrix(machine.properties, 1)
    m.add('p1','p3',2)
    m.add('p3','p1',2)
    machine['setup'] = m
    initialize_control(model)
    return model

def initialize_control(model):
    model.register_control(ControlCreate)
    model.register_control(ControlMachine)

def start(model):
    model.emulate(until=44)
  
def step():
    emulate(tempo=0.05, until=40)

if __name__ == '__main__': 
    model = create_model()
    start(model)
