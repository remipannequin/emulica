#! /usr/bin/python
# *-* coding: utf8 *-*

import sys, gtk
sys.path.insert(0, "../src/")
from emulica import emulicapp
import sim4 as sim

model = sim.create_model()
d = emulicapp.ModuleSelectionDialog(model.modules, None)
d.run()
d.destroy()
