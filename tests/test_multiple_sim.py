
import sys, logging
sys.path.insert(0,"../src")
from emulica import emulation

import sim1 as sim
#we create a model (sim1 for exemple)
model = sim.create_model()
#run it one time
print "simulation 1"
model.emulate(until = 100)
for (pid, p) in model.products.items():
    print (pid, p.shape_history, p.space_history, p.create_time, p.dispose_time)
#and one more time !
print "simulation 2"
model.emulate(until = 20)
for (pid, p) in model.products.items():
    print (pid, p.shape_history, p.space_history, p.create_time, p.dispose_time)
