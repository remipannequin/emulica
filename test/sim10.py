#! /usr/bin/python
# *-* coding: utf8 *-*

"""
In this test model, we use assemble actuators...
two type of products are created, and then assembled, and finally put in inventory



Create1----->source1----->assy_holder----->sink
                             ^
                             |
                            Assy
                             |
          Create2---->source2+

Control cycle:

wait source1
move from source1 to assy_space (load)
wait source2
wait assy_space
assemble with source2
move from assy_sapce to sink (unload)
"""

import sys, logging
sys.path.insert(0,"../src")
from emulica import emulation
logger = logging.getLogger('sim10')

exp_result_resource = [[(0, 0, 'setup'), 
                        (0, 2, 'load'), 
                        (7, 7, 'setup'), 
                        (7, 8, 'unload'), 
                        (8, 8, 'setup'), 
                        (8, 10, 'load'), 
                        (15, 15, 'setup'), 
                        (15, 16, 'unload'), 
                        (16, 16, 'setup'), 
                        (16, 18, 'load'), 
                        (23, 23, 'setup'), 
                        (23, 24, 'unload'), 
                        (24, 24, 'setup'), 
                        (24, 26, 'load'), 
                        (31, 31, 'setup'), 
                        (31, 32, 'unload'), 
                        (32, 32, 'setup'), 
                        (32, 34, 'load'), 
                        (39, 39, 'setup'), 
                        (39, 40, 'unload'), 
                        (40, 40, 'setup'), 
                        (40, 42, 'load'), 
                        (47, 47, 'setup'), 
                        (47, 48, 'unload'), 
                        (48, 48, 'setup'), 
                        (48, 50, 'load'), 
                        (55, 55, 'setup'), 
                        (55, 56, 'unload')], 
                       [(2, 2, 'setup'),
                        (2, 7, 'p'),
                        (10, 15, 'p'), 
                        (18, 23, 'p'),
                        (26, 31, 'p'),
                        (34, 39, 'p'),
                        (42, 47, 'p'),
                        (50, 55, 'p')]]

exp_result_product = [(1, [], [(0, 'source1'), (0, 'trans'), (2, 'assy_space'), (7, 'trans'), (8, 'sink')], 0, 56), 
                      (2, [], [(0, 'source1'), (8, 'trans'), (10, 'assy_space'), (15, 'trans'), (16, 'sink')], 0, 56), 
                      (3, [], [(0, 'source1'), (16, 'trans'), (18, 'assy_space'), (23, 'trans'), (24, 'sink')], 0, 56), 
                      (4, [], [(0, 'source1'), (24, 'trans'), (26, 'assy_space'), (31, 'trans'), (32, 'sink')], 0, 56), 
                      (5, [], [(0, 'source1'), (32, 'trans'), (34, 'assy_space'), (39, 'trans'), (40, 'sink')], 0, 56), 
                      (6, [], [(0, 'source1'), (40, 'trans'), (42, 'assy_space'), (47, 'trans'), (48, 'sink')], 0, 56), 
                      (7, [], [(0, 'source1'), (48, 'trans'), (50, 'assy_space'), (55, 'trans'), (56, 'sink')], 0, 56), 
                      (8, [], [(0, 'source2'), (2, 'assy_space'), (7, 'trans'), (8, 'sink')], 0, 56), 
                      (9, [], [(0, 'source2'), (10, 'assy_space'), (15, 'trans'), (16, 'sink')], 0, 56), 
                      (10, [], [(0, 'source2'), (18, 'assy_space'), (23, 'trans'), (24, 'sink')], 0, 56), 
                      (11, [], [(0, 'source2'), (26, 'assy_space'), (31, 'trans'), (32, 'sink')], 0, 56), 
                      (12, [], [(0, 'source2'), (34, 'assy_space'), (39, 'trans'), (40, 'sink')], 0, 56), 
                      (13, [], [(0, 'source2'), (42, 'assy_space'), (47, 'trans'), (48, 'sink')], 0, 56), 
                      (14, [], [(0, 'source2'), (50, 'assy_space'), (55, 'trans'), (56, 'sink')], 0, 56)]

class ControlCreate(emulation.Process):
    def run(self, model):
        create1 = model.modules["create1"] 
        create2 = model.modules["create2"] 
        rp_crea1 = create1.create_report_socket()
        rp_crea2 = create2.create_report_socket()
        dates1 = [0, 1, 3, 7, 12, 20, 30]
        requests1 = [emulation.Request("create1", "create",params={'productType':'type1', 'date': d}) for d in dates1]
        dates2 = [5, 6, 7, 9, 11, 23, 35]
        requests2 = [emulation.Request("create2", "create",params={'productType':'type1', 'date': d}) for d in dates2]
        yield emulation.put, self, create1.request_socket, requests1
        yield emulation.get, self, rp_crea1, 7
        yield emulation.put, self, create2.request_socket, requests2
        yield emulation.get, self, rp_crea2, 7

class ControlAssy(emulation.Process):
    def run(self, model):
        trans = model.modules["trans"]
        assy = model.modules["assy"]
        rp_assy = assy.create_report_socket()
        obs1 = model.modules["obs_source1"]
        obs2 = model.modules["obs_source2"]
        rp_obs1 = obs1.create_report_socket()
        rp_obs2 = obs2.create_report_socket()
        obs_assy = model.modules["obs_assy"]
        rp_obs_assy = obs_assy.create_report_socket()
        while True:
            ##attente de l'arrivée d'un pièce
            logger.info("attente d'une piece")
            yield emulation.get, self, rp_obs1, 1
            logger.info("pce 1 prete")
            ev = self.got[0]
            logger.info("chargement")
            rq = emulation.Request("trans","move",params={'program':'load'})
            yield emulation.put, self, trans.request_socket, [rq]
            ##pièces prêtes
            yield emulation.get, self, rp_obs2, 1
            logger.info("pce 2 prete")
            yield emulation.get, self, rp_obs_assy, 1
            logger.info("pce assy chargée")
            #print self.got[0]
            #yield emulation.put, self, assy.request_socket, [emulation.Request("assy","setup", params={"program":'p'})]
            ##début process
            logger.info("process")
            yield emulation.put, self, assy.request_socket, [emulation.Request("assy","assy", params={"program":'p'})]
            ##attente fin process
            fin = False
            while not fin:
                yield emulation.get, self, rp_assy, 1
                logger.info(self.got[0])
                fin = self.got[0].what=="idle"
            ##déchargement
            logger.info("dechargement")
            yield emulation.put, self, trans.request_socket, [emulation.Request("trans", "move", params={"program": 'unload'})]

def create_model():
    model = emulation.Model()
    source1 = emulation.Holder(model, "source1")
    obs_source1 = emulation.PushObserver(model, "obs_source1", holder = source1)
    source2 = emulation.Holder(model, "source2")
    obs_source2 = emulation.PushObserver(model, "obs_source2", holder = source2)
    create1 = emulation.CreateAct(model, "create1", destination = source1)
    create2 = emulation.CreateAct(model, "create2", destination = source2)
    assy_space = emulation.Holder(model, "assy_space")
    obs_assy = emulation.PushObserver(model, "obs_assy", holder = assy_space)
    assy = emulation.AssembleAct(model, "assy", assy_holder = assy_space)
    trans = emulation.SpaceAct(model, "trans")
    sink = emulation.Holder(model, "sink")
    obs_sink = emulation.PushObserver(model, "obs_sink", holder = sink)
    trans.add_program('load', 2, {'source':source1, 'destination':assy_space})
    trans.add_program('unload', 1, {'source':assy_space, 'destination':sink})
    assy.add_program('p', 5, {'source':source2})
    initialize_control(model)
    return model

def initialize_control(model):
    model.register_control(ControlCreate)
    model.register_control(ControlAssy)
    
def start(model):
    model.emulate(until = 100)

def main():
    console = logging.StreamHandler()
    logging.getLogger().setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    model = create_model()
    start(model)
    for (pid, p) in model.products.items():
        print (pid, p.shape_history, p.space_history, p.create_time, p.dispose_time)

if __name__ == '__main__': main()
