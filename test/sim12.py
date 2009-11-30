#! /usr/bin/python
# *-* coding: utf8 *-*

"""
This simple model based on sim1 tests the insert_request(): test of out-of-simulation request insertion
"""

import sys
sys.path.insert(0, "../src/")
import time
import threading
import emulica.emulation as emu
from emulica import controler

exp_result = [(1, [], [(5, 'holder1')], 5, 30),
              (2, [], [(15, 'holder1')], 15, 30),
              (3, [], [(30, 'holder1')], 30, 30)]
        
def create_model():
    model = emu.Model()
    h = emu.Holder(model, "holder1")
    c = emu.CreateAct(model, "create1", h)
    return model
  
def start(model):
    model.emulate(until = 100)

def step(model):
    model.emulate(until = 100, speed = 2, real_time = True)

def main():
    model = create_model()
    finished = threading.Condition()
    def release_condition(model):
        finished.acquire()
        finished.notify()
        finished.release()
    timer = controler.TimeControler(model, real_time = True, rt_factor = 1, until = 100)
    timer.add_callback(release_condition, controler.EVENT_FINISHED)
    timer.start()
 
    rq = emu.Request("create1", "create")
    #attente de 5s et ajout d'une requête de la simulation
    time.sleep(5)
    print "insert at 5"
    timer.dispatch(emu.Request("create1", "create", date = 5))
    #attente 10s et ajout
    time.sleep(10)
    print "insert at 15"
    timer.dispatch(emu.Request("create1", "create", date = 15))
    #attente 15s et ajout
    time.sleep(15)
    print "insert at 30"
    timer.dispatch(emu.Request("create1", "create", date = 30))
    #attente de fin de simulation...
    finished.acquire()
    finished.wait()
    finished.release()
    for (pid, p) in model.products.items():
        print (pid, p.shape_history, p.space_history, p.create_time, p.dispose_time)

if __name__ == '__main__': main()
  
