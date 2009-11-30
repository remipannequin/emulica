#! /usr/bin/python
# *-* coding: utf8 *-*

"""
In this very simple example, we create the mot simple model possible:
a create actuator put some product in a holder. These product trigger 
a dispose actuator thanks to a product observer on the holder.

"""

import sys
sys.path.insert(0, "../src/")

RT = True
import emulica.emulation as emu

exp_result = [(1, [], [(0, 'holder1')], 0, 4),
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

def create_model():
    model = emu.Model()
    h = emu.Holder(model, "holder1")
    obs1 = emu.PushObserver(model, "observer1", "ev1", observe_type = False, holder = h)
    c = emu.CreateAct(model, "create1", h)
    d = emu.DisposeAct(model, "dispose1", h)
    #control processes
    initialize_control(model)
    return model

def initialize_control(model):
    model.register_control(ControlCreate)
    model.register_control(ControlDispose)
    
def start(model):
    model.emulate(until = 100)

def step(model):
    model.emulate(until = 100, speed = 2, real_time = True)

def main():
  model = create_model()
  start(model)
  for (pid, p) in model.products.items():
    print (pid, p.shape_history, p.space_history, p.create_time, p.dispose_time)

if __name__ == '__main__': main()
  
