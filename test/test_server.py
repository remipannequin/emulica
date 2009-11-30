#! /usr/bin/python
# *-* coding: utf8 *-*
import sys
sys.path.insert(0,"../src/")

from emulica import controler
import sim12

model = sim12.create_model()


serv = controler.EmulationServer(model, 51000)
serv.start()
