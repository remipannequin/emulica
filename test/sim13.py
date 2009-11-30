#! /usr/bin/python
# *-* coding: utf8 *-*

"""
In this model, we test if the same report socket can be created and attached to several modules.
"""

import sys
sys.path.insert(0, "../src/")

RT = True
import emulica.emulation as emu

exp_report_list = [emu.Report("create1", "create-done", date = d*10) for d in range(11)]
exp_report_list.insert(1, emu.Report("observer1", "ev1", location = "holder1", date = 0))
report_list = []
                  
class ControlCreate(emu.Process):
    def run(self, model):
        n = 0
        createModule = model.modules["create1"]
        while n < 10:
            m = emu.Request("create1", "create")
            yield emu.put, self, createModule.request_socket, [m]
            yield emu.hold, self, 10

class ReportMonitor(emu.Process):
    def run(self, model):
        """PEM : create a Store, and attach it to every module in the model"""
        queue = emu.Store()
        for module in model.modules.values():
            module.attach_report_socket(queue)
        while True:
            yield emu.get, self, queue, 1
            report = self.got[0]
            report_list.append(report)

def create_model():
    model = emu.Model()
    h = emu.Holder(model, "holder1")
    obs1 = emu.PushObserver(model, "observer1", "ev1", observe_type = False, holder = h)
    c = emu.CreateAct(model, "create1", h)
    #control processes
    initialize_control(model)
    return model

def initialize_control(model):
    model.register_control(ControlCreate)
    model.register_control(ReportMonitor)
    
def start(model):
    model.emulate(until = 100)

def step(model):
    model.emulate(until = 100, speed = 2, real_time = True)

def main():
  model = create_model()
  start(model)
  print report_list

if __name__ == '__main__': main()
  
