#! /usr/bin/python
# *-* coding: utf8 *-*

"""
This simple model based on sim1 tests the insert_request() method of emulation.Model
"""

import sys
sys.path.insert(0, "../src/")

RT = True
import emulica.emulation as emu

exp_result = [(1, [], [(5, 'holder1')], 5, 30),
              (2, [], [(15, 'holder1')], 15, 30),
              (3, [], [(30, 'holder1')], 30, 30)]
                  
class ControlCreate(emu.Process):
    def run(self, model):
        rq = emu.Request("create1", "create")
        yield emu.hold, self, 5
        model.insert_request(rq)
        yield emu.hold, self, 10
        model.insert_request(rq)
        yield emu.hold, self, 15
        model.insert_request(rq)
        
def create_model():
    model = emu.Model()
    h = emu.Holder(model, "holder1")
    c = emu.CreateAct(model, "create1", h)
    initialize_control(model)
    return model

def initialize_control(model):
    model.register_control(ControlCreate)
    
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
  
