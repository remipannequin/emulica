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

exp_result = [(1, [], [(0. , 'holder1')], 0., 3.5),
              (2, [], [(2., 'holder1')], 2., 5.5), 
              (3, [], [(4., 'holder1')], 4., 7.0), 
              (4, [], [(5., 'holder1')], 5., 8.5), 
              (5, [], [(6., 'holder1')], 6., 10.), 
              (6, [], [(7., 'holder1')], 7., 11.5),
              (7, [], [(7.5, 'holder1')], 7.5, 13.),
              (8, [], [(8., 'holder1')], 8., 14.5)]
              
              
exp_result_position =  [(0.5, {4.0: 1}), 
                        (1.0, {3.0: 1}), 
                        (1.5, {2.0: 1}), 
                        (2, {1.0: 1, 5: 2}), 
                        (2.5, {0: 1, 4.0: 2}), 
                        (3.0, {0: 1, 3.0: 2}), 
                        (3.5, {2.0: 2}), 
                        (4.0, {1.0: 2, 4.0: 3}), 
                        (4.5, {0: 2, 3.0: 3}), 
                        (5.0, {0: 2, 2.0: 3, 4.0: 4}), 
                        (5.5, {1.0: 3, 3.0: 4}), 
                        (6.0, {0: 3, 2.0: 4, 4.0: 5}), 
                        (6.5, {0: 3, 1: 4, 3.0: 5}), 
                        (7.0, {1.0: 4, 2.0: 5, 4.0: 6}), 
                        (7.5, {0: 4, 1: 5, 3.0: 6, 4.0: 7}), 
                        (8.0, {0: 4, 1: 5, 2: 6, 3: 7, 4: 8}), 
                        (8.5, {1.0: 5, 2.0: 6, 3.0: 7, 4.0: 8}), 
                        (9.0, {0: 5, 1: 6, 2: 7, 3: 8}), 
                        (9.5, {0: 5, 1: 6, 2: 7, 3: 8}), 
                        (10.0, {1.0: 6, 2.0: 7, 3.0: 8}), 
                        (10.5, {0: 6, 1: 7, 2: 8}), 
                        (11.0, {0: 6, 1: 7, 2: 8}), 
                        (11.5, {1.0: 7, 2.0: 8}), 
                        (12.0, {0: 7, 1: 8}), 
                        (12.5, {0: 7, 1: 8}), 
                        (13.0, {1.0: 8}), 
                        (13.5, {0: 8}), 
                        (14.0, {0: 8}), 
                        (14.5, {}), 
                        (15.0, {}), 
                        (15.5, {}), 
                        (16.0, {})]

pos_list = list()

class ControlCreate(emu.Process):
    def run(self, model):
        createModule = model.modules["create1"]
        requests = [emu.Request("create1", "create", date = t) for t in [0., 2., 4., 5., 6., 7., 7.5, 8.]]
        yield emu.put, self, createModule.request_socket, requests
                    

class ControlDispose(emu.Process):
    def run(self, model):
        disposeModule = model.modules["dispose1"]
        observerModule = model.modules["observer1"]
        report = observerModule.create_report_socket()
        while True:
            yield emu.get, self, report, 1
            yield emu.put, self, disposeModule.request_socket, [emu.Request("dispose1","dispose", date = emu.now()+1)]

class ObsMonitor(emu.Process):
    def run(self, model):
        obs = model.modules["observer2"]
        report = obs.create_report_socket()
        while True:
            yield emu.put, self, obs.request_socket, [emu.Request("observer2","observe", date = emu.now() + 0.5)]
            yield emu.get, self, report, 1
            r = self.got[0]
            pos_list.append((r.when, r.how['ID_by_position']))
            
            
def create_model(stepping = False):
    pos_list = list()
    model = emu.Model()
    h = emu.Holder(model, "holder1")
    h['capacity'] = 5
    h['speed'] = 2
    obs1 = emu.PushObserver(model, "observer1", "ev1", observe_type = False, holder = h)
    obs2 = emu.PullObserver(model, "observer2", "position", holder = h)
    c = emu.CreateAct(model, "create1", h)
    d = emu.DisposeAct(model, "dispose1", h)
    initialize_control(model)
    return model

def initialize_control(model):
    model.register_control(ControlDispose)
    model.register_control(ControlCreate)
    model.register_control(ObsMonitor)

def start(model):
    model.emulate(until = 16)

def step(model):
    model.emulate(until = 100, speed = 2, real_time = True) 

if __name__ == '__main__': 
    model = create_model()
    start(model)
    result = [(pid, 
               p.shape_history, 
               p.space_history, 
               p.create_time, 
               p.dispose_time) for (pid, p) in model.products.items()]
    print result
    for (t, pos) in pos_list:
       print t, '\t', pos 
    print pos_list   
