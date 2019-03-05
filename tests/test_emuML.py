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


import unittest
import os
import util
util.set_path()

from xml.dom import minidom
from emulica.core import emuML, emulation

class TestConfig(unittest.TestCase):

    def compare_dom(self, s1, s2):
        """Util for emuML tests"""    
        dom1 = minidom.parseString(s1)
        dom2 = minidom.parseString(s2)
        dom1.normalize()
        dom2.normalize()
        return self.compare_node(dom1, dom2)

    def compare_node(self, dom1, dom2):
        """test if two DOM are "equivalent" 'ie have the same tree structure, regardless of the order of siblings
        """
        def node_cmp(n1): 
            node_id1 = n1.nodeName
            if 'getAttribute' in dir(n1) and n1.hasAttribute('name'):
                node_id1 += n1.getAttribute('name')
            return node_id1
            
        if not dom1.nodeType == dom2.nodeType:
            print(dom1.nodeType, dom2.nodeType)
            print(dom1.toxml())
            print(dom2.toxml())
            return False
        if not dom1.nodeName == dom2.nodeName: 
            print(dom1.nodeName, dom2.nodeName)
            print(dom1.toxml())
            print(dom2.toxml())
            return False
        if dom1.nodeValue == None:
            if not dom1.nodeValue == dom2.nodeValue:
                print(dom1.nodeValue, dom2.nodeValue)
                print(dom1.toxml())
                print(dom2.toxml())
                return False
        else:
            if not dom1.nodeValue.strip() == dom2.nodeValue.strip(): 
                print (dom1.nodeValue.strip(), dom2.nodeValue.strip())
                return False
        l1 = sorted(dom1.childNodes, key=node_cmp)
        l2 = sorted(dom2.childNodes, key=node_cmp)
        if not len(l1) == len(l2):
            print("number of childs:", len(l1), len(l2))
            print(dom1.toxml())
            print(dom2.toxml())
            return False
        test = True
        for i in range(len(l1)):
            test = test and self.compare_node(l1[i],l2[i])
        return test

    def test_config1(self):
        """test emuML with create dispose, holder and push observer"""
        import test_sim1 as sim
        
        m1 = sim.get_model()
        efile = emuML.EmulationWriter(m1)
        output = efile.write()
        f = open(os.path.join(os.path.dirname(__file__), 'data', "sim1.xml"),'r')
        exp_output = f.read()
        f.close()
        self.assertTrue(self.compare_dom(output, exp_output))
        
        m2 = emuML.load(os.path.join(os.path.dirname(__file__), 'data', "sim1.xml"))
        output = emuML.save(m2)
        self.assertTrue(self.compare_dom(output, exp_output))
        
        m3 = emuML.load(os.path.join(os.path.dirname(__file__), 'data', "sim1.xml"))
        sim.register_control(m3)
        m3.emulate(until= sim.EMULATE_UNTIL)
        result = [(pid, 
                   p.shape_history, 
                   p.space_history, 
                   p.create_time, 
                   p.dispose_time) for (pid, p) in m3.products.items()]
        self.assertEqual(result, sim.EXP_RESULT)
        
    def test_config2(self):
        """test emuML with create, space, shape, pushobserver"""
        import test_sim4 as sim
        m1 = sim.get_model()
        output = emuML.save(m1)
        #test whether output equals sim4.xml...
        f = open(os.path.join(os.path.dirname(__file__), 'data', "sim4.xml"),'r')
        exp_output = f.read()
        f.close()
        self.assertTrue(self.compare_dom(output, exp_output))
        m2 = emuML.load(os.path.join(os.path.dirname(__file__), 'data', "sim4.xml"))
        output = emuML.save(m2)
        self.assertTrue(self.compare_dom(output, exp_output))
        m3 = emuML.load(os.path.join(os.path.dirname(__file__), 'data', "sim4.xml"))
        sim.register_control(m3)
        
        m3.emulate(until = sim.EMULATE_UNTIL)
        result_product = [(pid, p.shape_history, 
                       p.space_history, 
                       p.create_time, 
                       p.dispose_time) for (pid, p) in m3.products.items()]
        result_resource = [m3.modules["transporter"].trace, m3.modules["machine"].trace]
        self.assertEqual(result_product, sim.EXP_RESULT_PRODUCT)
        self.assertEqual(result_resource, sim.EXP_RESULT_RESOURCE)

    def test_config3(self):
        """test emuML with create, holder, pushobserver, failure"""
        import test_sim7 as sim
        sim_file = os.path.join(os.path.dirname(__file__), 'data', "sim7.xml")
        m1 = sim.get_model()
        output = emuML.save(m1)
        #test whether output equals sim4.xml...
        f = open(sim_file,'r')
        exp_output = f.read()
        f.close()
        self.assertTrue(self.compare_dom(output, exp_output))
        m2 = emuML.load(sim_file)
        output = emuML.save(m2)
        self.assertTrue(self.compare_dom(output, exp_output))
        m3 = emuML.load(sim_file)
        sim.register_control(m3)
        m3.emulate(until = sim.EMULATE_UNTIL)
        result_product = [(pid, p.shape_history, 
                           p.space_history, 
                           p.create_time, 
                           p.dispose_time) for (pid, p) in m3.products.items()]
        result_resource = [m3.modules["transporter"].trace, m3.modules["machine"].trace]
        self.assertEqual(result_product, sim.EXP_RESULT_PRODUCT)
        self.assertEqual(result_resource, sim.EXP_RESULT_RESOURCE)

    def test_config4(self):
        """test emuML with create, holder with speed and capacity, pushobserver, pullobserver"""
        import test_sim8 as sim
        sim_file = os.path.join(os.path.dirname(__file__), 'data', "sim8.xml")
        m1 = sim.get_model()
        output = emuML.save(m1)
        #test whether output equals sim4.xml...
        f = open(sim_file,'r')
        exp_output = f.read()
        f.close()
        self.assertTrue(self.compare_dom(output, exp_output))
        m2 = emuML.load(sim_file)
        output = emuML.save(m2)
        self.assertTrue(self.compare_dom(output, exp_output))
        m3 = emuML.load(sim_file)
        sim.register_control(m3)
        m3.emulate(until = sim.EMULATE_UNTIL)
        result = [(pid, 
               p.shape_history, 
               p.space_history, 
               p.create_time, 
               p.dispose_time) for (pid, p) in m3.products.items()]
        self.assertEqual(result, sim.EXP_RESULT)


    def test_config5(self):
        """Test emuML with physical properties"""
        import test_sim14 as sim
        sim_file = os.path.join(os.path.dirname(__file__), 'data', "sim14.xml")
        m1 = sim.get_model()
        output = emuML.save(m1)
        #test whether output equals sim4.xml...
        f = open(sim_file,'r')
        exp_output = f.read()
        f.close()
        self.assertTrue(self.compare_dom(output, exp_output))
        m2 = emuML.load(sim_file)
        output = emuML.save(m2)
        self.assertTrue(self.compare_dom(output, exp_output))
        m3 = emuML.load(sim_file)
        sim.register_control(m3)
        m3.emulate(until = sim.EMULATE_UNTIL)
        result = [(pid, 
                   p.shape_history, 
                   p.space_history,
                   dict([(key, p[key]) for key in p.properties.keys()]),
                   p.create_time, 
                   p.dispose_time) for (pid, p) in m3.products.items()]
        result_resource = [m3.modules["transporter"].trace, m3.modules["machine"].trace]
        self.assertEqual(result, sim.EXP_RESULT_PRODUCT)
        self.assertEqual(result_resource, sim.EXP_RESULT_RESOURCE)

    def test_config6(self):
        import test_sim15 as sim
        m1 = sim.get_model()
        sim_file = os.path.join(os.path.dirname(__file__), 'data', "sim15.xml")
        output = emuML.save(m1)
        f = open(sim_file,'r')
        exp_output = f.read()
        f.close()
        self.assertTrue(self.compare_dom(output, exp_output))
        
        m3 = emuML.load(sim_file)
        #sim.register_control_submodel(m3.modules['cell'])
        sim.register_control(m3)
        m3.emulate(until = sim.EMULATE_UNTIL)
        result = [(pid, 
                   p.shape_history, 
                   p.space_history,
                   p.create_time, 
                   p.dispose_time) for (pid, p) in m3.products.items()]
        result_resource = [m3.get_module("cell.transporter").trace, m3.get_module("cell.machine").trace]
        self.assertEqual(result, sim.EXP_RESULT_PRODUCT)
        self.assertEqual(result_resource, sim.EXP_RESULT_RESOURCE)
        
        
    
    
    
if __name__ == '__main__':
    unittest.main()



