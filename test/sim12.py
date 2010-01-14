#! /usr/bin/python
# *-* coding: utf8 *-*

"""
This simple model based on sim1 tests the insert_request(): test of out-of-simulation request insertion
"""

import sys
sys.path.insert(0, "../src/")
import time
import threading
from emulica.emulation import *
from emulica import controler

exp_result = [(1, [], [(5, 'holder1')], 5, 30),
              (2, [], [(15, 'holder1')], 15, 30),
              (3, [], [(30, 'holder1')], 30, 30)]
        
class ControlProcess(Process):
    def run(self, model):
        """Listen to request sent to the model (name 'main'), requesting 'do', 
        create a product when receiving such request."""
        create = model.get_module("create1")
        create
        while True:
            print "waiting for event to arrive to request queue of model"
            yield get, self, model.request_socket, 1
            ev = self.got[0]
            print "got event !"
            yield put, self, create.request_socket, [Request("create1", "create")]
            
        
        
def create_model():
    model = Model()
    h = Holder(model, "holder1")
    c = CreateAct(model, "create1", h)
    o = PushObserver(model, "obs", "ev1", observe_type = False, holder = h)
    return model
  

  
def initialize_control(model):
    model.register_control(ControlProcess)
    
    
  
def start(model):
    model.emulate(until = 100)

def step(model):
    model.emulate(until = 100, speed = 10, real_time = True)

def main():
    model = create_model()
    finished = threading.Condition()
    def release_condition(model):
        finished.acquire()
        finished.notify()
        finished.release()
    timer = controler.TimeControler(model, real_time = True, rt_factor = 10, until = 100)
    timer.add_callback(release_condition, controler.EVENT_FINISH)
    timer.start()
 
    #attente de 5s et ajout d'une requête de la simulation
    print "insert at 5"
    timer.dispatch(emu.Request("create1", "create", date = 5))
    #attente 10s et ajout
    time.sleep(0.1)
    print "insert at 15"
    timer.dispatch(emu.Request("create1", "create", date = 15))
    #attente 15s et ajout
    time.sleep(2)
    print "insert at 30"
    timer.dispatch(emu.Request("create1", "create", date = 30))
    #attente de fin de simulation...
    finished.acquire()
    finished.wait()
    finished.release()
    for (pid, p) in model.products.items():
        print (pid, p.shape_history, p.space_history, p.create_time, p.dispose_time)

if __name__ == '__main__': main()
  
