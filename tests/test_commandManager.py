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
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from emulica import emulation, properties
from emulica.CommandManager import CommandManager


class TestCommandManager(unittest.TestCase):
    
    def setUp(self):
        import test_sim14 as sim
        self.model = sim.get_model()
        
    def test_Init(self):
        cmd = CommandManager()
        #verify the can undo and can redo return false
        self.assertFalse(cmd.can_undo())
        self.assertFalse(cmd.can_redo())
        
    def test_Create(self):
        cmd = CommandManager()
        cmd.create_module('test_module', emulation.CreateAct, self.model)
        #verify that the module has been created
        module = self.model.modules['test_module']
        self.assertIsInstance(module, emulation.CreateAct)
        self.assertTrue(cmd.can_undo())
        self.assertFalse(cmd.can_redo())
        cmd.undo()
        self.assertNotIn('test_module', self.model.modules.keys())
        self.assertFalse(cmd.can_undo())
        self.assertTrue(cmd.can_redo())
        cmd.redo()
        module2 = self.model.modules['test_module']
        self.assertEqual(module, module2)
        self.assertTrue(cmd.can_undo())
        self.assertFalse(cmd.can_redo())
        
    def test_Rename(self):
        cmd = CommandManager()
        cmd.create_module('test_module', emulation.CreateAct, self.model)
        module = self.model.modules['test_module']
        cmd.rename_module(module, 'test_module2')
        module3 = self.model.modules['test_module2']
        self.assertIs(module3, module)
        self.assertEqual(module3.name,'test_module2')
        self.assertNotIn('test_module', self.model.modules.keys())
        self.assertIn('test_module2', self.model.modules.keys())
        cmd.undo()
        self.assertEqual(module3.name,'test_module')
        self.assertIn('test_module', self.model.modules.keys())
        self.assertNotIn('test_module2', self.model.modules.keys())
        cmd.redo()
        self.assertEqual(module3.name,'test_module2')
        self.assertNotIn('test_module', self.model.modules.keys())
        self.assertIn('test_module2', self.model.modules.keys())
        
    def test_Delete(self):
        cmd = CommandManager()
        cmd.create_module('test_module', emulation.CreateAct, self.model)
        module = self.model.modules['test_module']
        cmd.delete_module(module, self.model)
        #verify module has been deleted
        self.assertNotIn('test_module', self.model.modules.keys())
        cmd.undo()
        self.assertIn('test_module', self.model.modules.keys())
        cmd.redo()
        self.assertNotIn('test_module', self.model.modules.keys())
        
        
    def test_ChangeProperty(self):
        cmd = CommandManager()
        create = self.model.modules['create']
        source = self.model.modules['source']
        sink = self.model.modules['sink']
        cmd.change_prop(create.properties, 'destination', sink)
        self.assertIs(create.properties['destination'], sink)
        cmd.undo()
        self.assertIs(create.properties['destination'], source)
        cmd.redo()
        self.assertIs(create.properties['destination'], sink)
        
    
    def test_AddProgram(self):
        cmd = CommandManager()
        machine = self.model.modules['machine']
        cmd.add_prog(machine.properties['program_table'], 'p4', 4, {'change': {'length': 1}})
        self.assertIn('p4', machine.properties['program_table'])
        p = machine.properties['program_table']['p4']
        self.assertIs(machine.properties['program_table']['p4'], p)
        cmd.undo()
        self.assertNotIn('p4', machine.properties['program_table'])
        cmd.redo()
        self.assertIn('p4', machine.properties['program_table'])
        self.assertIs(machine.properties['program_table']['p4'], p)
    
    
    def test_ChangeProgram(self):
        cmd = CommandManager()
        machine = self.model.modules['machine']
        cmd.add_prog(machine.properties['program_table'], 'p4', 4, {'change': {'length': 1}})
        p = machine.properties['program_table']['p4']
        cmd.change_prog_time(p, 12)
        self.assertEqual(p.time(), 12)
        cmd.undo()
        self.assertEqual(p.time(), 4)
        cmd.redo()
        self.assertEqual(p.time(), 12)
    
    def test_ChangeProgName(self):
        cmd = CommandManager()
        machine = self.model.modules['machine']
        
        cmd.add_prog(machine.properties['program_table'], 'p4', 4, {'change': {'length': 1}})
        p = machine.properties['program_table']['p4']
        cmd.change_prog_name(machine.properties['program_table'], 'p4', 'p4bis')
        self.assertIn('p4bis', machine.properties['program_table'])
        self.assertNotIn('p4', machine.properties['program_table'])
        self.assertIs(machine.properties['program_table']['p4bis'], p)
        cmd.undo()
        self.assertNotIn('p4bis', machine.properties['program_table'])
        self.assertIn('p4', machine.properties['program_table'])
        self.assertIs(machine.properties['program_table']['p4'], p)
        cmd.redo()
        self.assertIn('p4bis', machine.properties['program_table'])
        self.assertNotIn('p4', machine.properties['program_table'])
        self.assertIs(machine.properties['program_table']['p4bis'], p)
    
    def test_RemoveProg(self):
        cmd = CommandManager()
        machine = self.model.modules['machine']
        cmd.add_prog(machine.properties['program_table'], 'p4', 4, {'change': {'length': 1}})
        p = machine.properties['program_table']['p4']
        cmd.del_prog(machine.properties['program_table'], 'p4')
        self.assertNotIn('p4', machine.properties['program_table'])
        cmd.undo()
        self.assertIn('p4', machine.properties['program_table'])
        self.assertIs(machine.properties['program_table']['p4'], p)
        cmd.redo()
        self.assertNotIn('p4', machine.properties['program_table'])
    
    def test_AddSetup(self):
        cmd = CommandManager()
        machine = self.model.modules['machine']
        p1 = machine.properties['program_table']['p1']
        p2 = machine.properties['program_table']['p2']
        m = machine.properties['setup']
        cmd.add_setup(m, p1, p2, 3)
        self.assertEqual(m.get(p1, p2), 3)
        cmd.undo()
        self.assertEqual(m.get(p1, p2), 1)
        cmd.redo()
        self.assertEqual(m.get(p1, p2), 3)
        
    
    def test_ChangeSetup(self):
        cmd = CommandManager()
        machine = self.model.modules['machine']
        p1 = machine.properties['program_table']['p1']
        p3 = machine.properties['program_table']['p3']
        m = machine.properties['setup']
        cmd.change_setup(m, p1, p3, new_time = 5)
        self.assertEqual(m.get(p1, p3), 5)
        cmd.undo()
        self.assertEqual(m.get(p1, p3), 2)
        cmd.redo()
        self.assertEqual(m.get(p1, p3), 5)
        
    def test_RemoveSetup(self):
        cmd = CommandManager()
        machine = self.model.modules['machine']
        p1 = machine.properties['program_table']['p1']
        p3 = machine.properties['program_table']['p3']
        m = machine.properties['setup']
        cmd.del_setup(m, p1, p3)
        self.assertEqual(m.get(p1, p3), 2)
        cmd.undo()
        self.assertEqual(m.get(p1, p3), 5)
        cmd.redo()
        self.assertEqual(m.get(p1, p3), 2)

if __name__ == '__main__':    
    unittest.main()




