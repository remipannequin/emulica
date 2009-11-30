#! /usr/bin/python
# *-* coding: utf8 *-*
"""Test loading a gseme file, setting some of its parameters, and getting the results"""

import sys, logging
#use devel version
sys.path.insert(0, '../../src')

from seme.semeML import GsemeFile, compile_control

def create_model(filename):
    gsfile = GsemeFile(filename, 'r')
    (model, control) = gsfile.read()
    compile_control(model, control)  
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

    model = create_model("looping.gseme")
    
    model.emulate(until=50)
    result_product = [(pid, p.shape_history, 
                       p.space_history, 
                       p.create_time, 
                       p.dispose_time) for (pid, p) in model.products.items()]
    
    print result_product
    
