#! /usr/bin/python
# *-* coding: utf8 *-*

"""This model tests the random number generation features.
"""

from __future__ import division

import sys
sys.path.insert(0, "../src/")
from emulica import emulation as emu
from emulica.emulation import Report, Request, put, get, Process, hold

class ControlCreate(Process):

    def run(self, model, a):
        n = 0
        createModule = model.modules["create1"]
        while True:
            m = Request("create1", "create")
            yield put, self, createModule.request_socket, [m]
            yield hold, self, model.rng.expovariate(a)
            n += 1


class ControlSpace(Process):
    def run(self, model):
        sp = model.modules["space1"]
        obs1 = model.modules["observer1"]
        rp_obs1 = obs1.create_report_socket()
        while True:
            yield get, self, rp_obs1, 1
            rq = Request("space1","move",params={'program':'p1'})
            yield put, self, sp.request_socket, [rq]


def create_model(a, b):
    model = emu.Model()
    h1 = emu.Holder(model, "h1")
    h2 = emu.Holder(model, "h2")
    obs1 = emu.PushObserver(model, "observer1", "ev1", holder = h1)
    obs2 = emu.PushObserver(model, "observer2", "ev2", holder = h2)
    c = emu.CreateAct(model, "create1", h1)
    sp = emu.SpaceAct(model, "space1")
    sp['setup'].default_time = 1 
    sp.add_program('p1', "rng.expovariate("+str(b)+")", {'source':h1, 'destination':h2})
    initialize_control(model, a)
    return model

def initialize_control(model, a):
    model.register_control(ControlCreate, 'run', (model, a))
    model.register_control(ControlSpace)

def run(a, b, seed, until = 250):
    model = create_model(a, b)   
    model.emulate(until, seed = seed)
    l = [(pid, p.create_time, p.dispose_time, 
          p.shape_history, p.space_history) for (pid, p) in model.products.items()]
    t = model.modules["space1"].trace
    m = model.modules["h1"].monitor.timeAverage()
    return (l, t, m)

def main():

    e = [(0.7, 976), (0.6, 9866), (0.5, 379786), (0.4, 74368), (0.3, 855427), (0.2, 875378), (0.1, 6532109)]
    s = list()
    replication = 100
    for i in range(replication):
        s.append([run(a, 1, seed+i*375, 500)[2] for (a, seed) in e])
        print "%d %%" % ((float(i)/replication)*100)
  
    print e
    print s
    print [sum([s[i][j] for i in range(replication)])/replication for j in range(len(e))]


if __name__ == '__main__': main()

