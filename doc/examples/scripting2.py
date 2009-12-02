#! /usr/bin/python
# *-* coding: utf8 *-*
"""Test loading a gseme file, setting some of its parameters, and getting the results.

This script accept one argument: an integer that is passed to the ControlCreate 
control process. This arg determine how many products will be created

"""

import sys, logging
#use devel version
sys.path.insert(0, '../../src')

from emulica.emuML import EmuFile, compile_control

def create_model(filename, nb_product):
    """Load the model from the emu file, and set the additionnal parameter 
    'nb_product' of the ControlCreate control process. 
    """
    gsfile = EmuFile(filename, 'r')
    (model, control) = gsfile.read()
    compile_control(model, control)
    new_control_classes = list()
    for (ctrl_class, method, args) in model.control_classes:
        if ctrl_class.__name__ == "ControlCreate":
            args = list(args)
            args.append(nb_product)
        new_control_classes.append((ctrl_class, method, args))
    model.control_classes = new_control_classes
    
    return model

def init_logger(level):
    console = logging.StreamHandler()
    logging.getLogger().setLevel(level)
    console.setLevel(level)
    formatter = logging.Formatter('%(name)-12s (%(lineno)d) : %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)

if __name__ == '__main__':

    
    init_logger(logging.DEBUG)
    if len(sys.argv) == 2:
        nb = int(sys.argv[1])
    else:
        nb = 10
    model = create_model("looping.emu", nb)
    
    model.emulate(until=50)
    result_product = [(pid, p.shape_history, 
                       p.space_history, 
                       p.create_time, 
                       p.dispose_time) for (pid, p) in model.products.items()]
    
    print result_product
    print len(model.products)
    
