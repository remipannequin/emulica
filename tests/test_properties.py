#!/usr/bin/env python

import sys
sys.path.insert(0, "../src/")
import sim14
from emulica import properties
import gtk

def main():
    model = sim14.create_model()
    
    for module in model.modules.values(): 
        win = properties.PropertiesDialog(None, module, model)

    gtk.main()
if __name__ == '__main__': main()
