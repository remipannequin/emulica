#!/usr/bin/python
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

import sys
import os.path
import unittest
import subprocess
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

#libs
from gi.repository import GooCanvas as goo
#from gi.repository import Gtk as gtk

#import classes required to run the test
from emulica import emulation
from emulica.canvas import *
from emulica.CommandManager import CommandManager

class TestCanvas(unittest.TestCase):
    def setUp(self):
        
        self.model = emulation.Model()
        self.cmd = CommandManager()
        
        # Open window to hold canvas.
        #self.win = gtk.Window(gtk.WindowType.TOPLEVEL)
        #self.win.connect('destroy', gtk.main_quit)
        #self.win.set_title('Test Canvas')
        # Create VBox to hold canvas and buttons.
        #self.vbox = gtk.VBox()
        #self.win.add(self.vbox)

    def show_win(self):
        self.win.show_all()
        gtk.main()
        
    
    def test_GooCanvas(self):
        """Just draw a rectangle in a canvas"""
        canvas = goo.Canvas()
        #self.vbox.add(canvas)
        canvas.set_size_request(300, 300)
        root = canvas.get_root_item()
        rect = goo.CanvasRect(parent = root,
                        x = 100,
                        y = 50,
                        width = 100,
                        height = 200,
                        line_width = 1,
                        fill_color = 'pale green')
    
    def test_ModuleLayer(self):
        canvas = goo.Canvas()
        #self.vbox.add(canvas)
        canvas.set_size_request(300, 300)
        root = canvas.get_root_item()
        ml = ModuleLayer(canvas, root, True)
    
    def testCreateCanvas(self):
        canvas = EmulicaCanvas(self.model, self.cmd)

    def unitModule(self, name, cls):
        canvas = EmulicaCanvas(self.model, self.cmd)
        #self.vbox.add(canvas)
        canvas.set_size_request(100, 50)
        h = cls(self.model, name)
        canvas.write_pdf(name+'.pdf')
        return_code = subprocess.call(["diff", name+'.pdf', 'tests/data/'+name+'.pdf'])
        self.assertEqual(return_code, 0)
        os.remove(name+'.pdf')

    def testHolder(self):
        self.unitModule('holder', emulation.Holder)
    
    def testCreate(self):
        self.unitModule('create', emulation.CreateAct)
        
    def testDispose(self):
        self.unitModule('dispose', emulation.DisposeAct)
    
    def testAssy(self):
        self.unitModule('assy', emulation.AssembleAct)
    
    def testUnAssy(self):
        self.unitModule('unassy', emulation.DisassembleAct)
        
    def testMove(self):
        self.unitModule('move', emulation.SpaceAct)
    
    def testMake(self):
        self.unitModule('make', emulation.ShapeAct)

    def testViewSim1(self):
        from test_sim1 import get_model
        
        model = get_model()
        
        canvas = EmulicaCanvas(self.model, self.cmd)
        #self.vbox.add(canvas)
        canvas.setup_model(model)
        canvas.apply_layout({model.get_module('create1'): (20,60), 
                             model.get_module('holder1'):(130,70),
                             model.get_module('dispose1'): (250, 60)})
        canvas.set_size_request(320, 200)
        canvas.write_pdf("sim1.pdf")
        return_code = subprocess.call(["diff", 'sim1.pdf', 'tests/data/sim1.pdf'])
        self.assertEqual(return_code, 0)
        os.remove('sim1.pdf')
        

if __name__ == '__main__':    
    unittest.main()
    print("test canvas")


