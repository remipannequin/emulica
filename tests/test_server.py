#! /usr/bin/python
# *-* coding: utf8 *-*
import sys
sys.path.insert(0,"../src/")

from emulica import controler
import sim12

model = sim12.create_model()
sim12.initialize_control(model)

serv = controler.EmulationServer(model, 51000)
print "begin server"
serv.start()
print "end of server"

for (pid, p) in model.products.items():
    print (pid, p.shape_history, p.space_history, p.create_time, p.dispose_time)
