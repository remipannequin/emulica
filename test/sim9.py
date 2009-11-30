#! /usr/bin/python
# *-* coding: utf8 *-*

"""
Real time / Hybrid time tests. Model based on sim1.
"""

import sys
sys.path.insert(0, "../src/")

import time
import threading
import emulica.emulation as emu
from emulica import controler

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
    def run(self, modules):
        n = 0
        createModule = modules["create1"]
        report = createModule.create_report_socket()
        while n < 10:
            m = emu.Request("create1", "create")
            yield emu.put, self, createModule.request_socket, [m]
            yield emu.get, self, report, 1
            yield emu.hold, self, 10

class ControlDispose(emu.Process):
    def run(self, modules):
        disposeModule = modules["dispose1"]
        observerModule = modules["observer1"]
        report = observerModule.create_report_socket()
        while True:
            yield emu.get, self, report, 1
            yield emu.put, self, disposeModule.request_socket, [emu.Request("dispose1","dispose",date=emu.now()+4)]

def create_model(stepping = False):
    model = emu.Model()
    h = emu.Holder(model, "holder1")
    obs1 = emu.PushObserver(model, "observer1", "ev1", observe_type = False)
    obs1.observe_holder(h)
    c = emu.CreateAct(model, "create1", h)
    d = emu.DisposeAct(model, "dispose1", h)
    #control processes
    controlDispose = ControlDispose()
    controlCreate = ControlCreate()
    emu.activate(controlCreate, controlCreate.run(model.modules))
    emu.activate(controlDispose, controlDispose.run(model.modules))
    return model

def main():
    model = create_model()
    finished = threading.Condition()
    def release_condition(model):
        finished.acquire()
        finished.notify()
        finished.release()
    
    timer = controler.TimeControler(model, real_time = True, rt_factor = 2, until = 100)
    timer.add_callback(release_condition, controler.EVENT_FINISH)
    timer.start()
    #attente de 20s et *pause* de la simulation
    time.sleep(20)
    timer.pause()
    #attente 10s et reprise
    time.sleep(10)
    timer.resume()
    
    
    #attente de fin de simulation...
    if not timer.finished:
         finished.acquire()
        finished.wait()
        finished.release()
    
    for (pid, p) in model.products.items():
        print (pid, p.shape_history, p.space_history, p.create_time, p.dispose_time)

if __name__ == '__main__': main()
  
