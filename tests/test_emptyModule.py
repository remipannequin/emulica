#!/usr/bin/python3
# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

import unittest

import util
util.set_path()

import logging
from emulica.core import set_up_logging
set_up_logging(logging.WARNING)

from emulica.core import emulation
from emulica.core.emulation import Request
import logging
logger = logging.getLogger('test_emptyModule')



EMULATE_UNTIL = 100;


class Control1:
    def run(self, model):
        while True:
            yield model.get_sim().timeout(5)
            rq = Request("mt", "test")
            print("insert request {} at {}".format(rq, model.current_time()))
            model.insert_request(rq)


class Control2:
    def run(self, model):
        mt = model.modules["mt"]
        while True:
            ev = yield mt.request_socket.get()
            print("Control: got {} at {}".format(ev, model.current_time()))


def get_model():
    model = emulation.Model()
    mt = emulation.EmptyModule(model, "mt")
    model.register_control(Control1)
    model.register_control(Control2)
    return model


class TestSim10(unittest.TestCase):
    def setUp(self):
        print(self.id())
        
    def test_ModelCreate(self):
        get_model()

    def test_Start(self):
        model = get_model()
        model.emulate(until = EMULATE_UNTIL)

    def test_RunResults(self):
        model = get_model()
        model.emulate(until = EMULATE_UNTIL)



if __name__ == '__main__':    
    unittest.main()
