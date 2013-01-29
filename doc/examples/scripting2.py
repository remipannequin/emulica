# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2013 Rémi Pannequin, Centre de Recherche en Automatique de Nancy remi.pannequin@univ-lorraine.fr
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

"""Test loading a gseme file, setting some of its parameters, and getting the results.

This script accept one argument: an integer that is passed to the ControlCreate 
control process. This arg determine how many products will be created

"""

import sys, logging
#use devel version
sys.path.insert(0, '../../src')

from emulica.emuML import EmuFile, compile_control

def create_model(filename, nb):
    """Load the model from the emu file, and set the additionnal parameter 
    'nb_product' of the ControlCreate control process. 
    """
    gsfile = EmuFile(filename, 'r')
    (model, control) = gsfile.read()
    compile_control(model, control, nb_product = nb)
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
    
