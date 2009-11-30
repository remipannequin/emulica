#!/usr/bin/env python
# *-* coding: iso-8859-15 *-*

# gui.py
# Copyright 2008, Rémi Pannequin, Centre de Recherche en Automatique de Nancy
# 
#
# This file is part of Emulica.
#
# Emulica is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Emulica is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Emulica.  If not, see <http://www.gnu.org/licenses/>.

import sys, getopt, logging, os

application = 'emulica'
import gettext
gettext.install(application)

from emulica import emuML, controler
from emulica.emulicapp import Emulica



DEFAULT_PORT = 51000

def usage():
    """Show usage information"""
    print(_("emulica is a GTK interface to emulica, an emulation modelling and execution framework"))
    print(_("usage: emulica -hd [emulica_file]"))
    print(_("usage: emulica --server --port num_port emulica_model.xml"))

def main(argv, script_dir):
    #Guess how we are being called
    if os.path.exists(os.path.join(script_dir, '../ui/emulica.ui')):
        #mode: source
        paths = {'ui_path': os.path.abspath(os.path.join(script_dir,'../ui')), 'icon_path': os.path.abspath(os.path.join(script_dir,'../ui'))}
    elif os.path.exists('/usr/share/emulica/emulica.ui'):
        paths = {'ui_path': os.path.abspath('/usr/share/emulica')}
    elif os.path.exists(os.path.join(script_dir, 'emulica.ui')):
        paths = {'ui_path': os.path.abspath(script_dir), 'icon_path': os.path.abspath(os.path.join(script_dir,'./icons'))}
    else:
        print(_("unable to find emulica.ui file, exiting."))
        sys.exit(1)
    
    
    try:
        opts, args = getopt.getopt(argv, "hdsp:=", ["help", "server", "port="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    #default values
    port = DEFAULT_PORT
    server = False
    console = logging.StreamHandler()
    logging.getLogger().setLevel(logging.WARNING)
    console.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(name)-12s (%(lineno)d) : %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()                  
            sys.exit()   
        elif opt in ("-s", "--server"):
            server = True
        elif opt in ("-p", "--port"):
            port = int(arg)  
        elif opt == '-d':
            logging.getLogger().setLevel(logging.DEBUG)
            console.setLevel(logging.DEBUG)
    if server:
        if len(args) > 0:
            model = semeML.load(args[0])
            app = controler.EmulationServer(model, port)
            app.start()
        else:
            print(_("in server mode, a model name must be provided"))
    else:
        app = Emulica(**paths)
        if len(args) > 0:
            app.main(args[0])
        else:
            app.main()



if __name__ == '__main__':
    p =  sys.argv[0]
    if not os.path.isabs(p):
        script_dir = os.path.dirname(os.path.abspath(p))
    else:
        script_dir = os.path.dirname(p)
    main(sys.argv[1:], script_dir)
