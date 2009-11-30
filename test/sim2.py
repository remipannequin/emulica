#! /usr/bin/python
# *-* coding: utf8 *-*
"""
Create -> holder -> space -> holder
"""

import sys
sys.path.insert(0, "../src/")
from emulica.emulation import *

exp_result_product = [(1, [], [(0, 'h1'), (0, 'space1'), (2, 'h2')], 0, 41),
                      (2, [], [(10, 'h1'), (10, 'space1'), (12, 'h2')], 10, 41),
                      (3, [], [(20, 'h1'), (20, 'space1'), (22, 'h2')], 20, 41),
                      (4, [], [(30, 'h1'), (30, 'space1'), (32, 'h2')], 30, 41),
                      (5, [], [(40, 'h1'), (40, 'space1')], 40, 41)]                  
exp_result_resource = [(0, 0, 'setup'), 
                       (0, 2, 'p1'), 
                       (10, 12, 'p1'), 
                       (20, 22, 'p1'), 
                       (30, 32, 'p1'), 
                       (40, 41, 'p1')]

class ControlCreate(Process):
    def run(self, model):
        n = 0
        createModule = model.modules["create1"]
        report = createModule.create_report_socket()
        while n < 10:
            m = Request("create1", "create")
            yield put, self, createModule.request_socket, [m]
            yield get, self, report, 1
            
            yield hold, self, 10


class ControlSpace(Process):
    def run(self, model):
        sp = model.modules["space1"]
        obs1 = model.modules["observer1"]
        report = obs1.create_report_socket()
        while True:
            yield get, self, report, 1
            ev = self.got[0]
            rq = Request("space1","move",params={'program':'p1'})
            yield put, self, sp.request_socket, [rq]
 
    
class MonitorSpace(Process):
    def run(self, model):
        sp = model.modules["space1"]
        report = sp.create_report_socket()
        while True:
            yield get, self, report, 1
            


def create_model():
    model = Model()
    h1 = Holder(model, "h1")
    h2 = Holder(model, "h2")
    obs1 = PushObserver(model, "observer1", "ev1", holder = h1)
    c = CreateAct(model, "create1", h1)
    sp = SpaceAct(model, "space1")
    sp.add_program('p1', 2, {'source':h1, 'destination':h2})
    initialize_control(model)
    return model

def initialize_control(model):
    model.register_control(ControlCreate)
    model.register_control(ControlSpace)
    model.register_control(MonitorSpace)
  
def start(model):
    model.emulate(until=41)
  
if __name__ == '__main__': 
    model = create_model()
    start(model)
