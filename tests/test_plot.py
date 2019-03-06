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

"""
This simple model based on sim1 tests the insert_request() method of emulation.Model
"""


import unittest
import imageio
import util
import os
util.set_path()

import emulica.core.emulation as emu
import emulica.core.plot as plot

EXP_RESULT = [(1, [], [(4, 'holder1')], 4, 25.0),
              (2, [], [(8, 'holder1')], 8, 25.0),
              (3, [], [(12, 'holder1')], 12, 25.0),
              (4, [], [(16, 'holder1')], 16, 25.0),
              (5, [], [(20, 'holder1')], 20, 25.0)]

EXP_MONITOR = [(2, 1), (4, 4.5), (7, 2), (10, 5)]

EMULATE_UNTIL = 25;

class ControlCreate:
    def run(self, model):
        rq = emu.Request("create1", "create")
        n = 0
        while n < 5:
            yield model.get_sim().timeout(4)
            yield model.modules['create1'].request_socket.put(rq)
            n += 1
        
def get_model():
    model = emu.Model()
    h = emu.Holder(model, "holder1")
    c = emu.CreateAct(model, "create1", h)
    model.register_control(ControlCreate)
    return model
    

class FakeSim(object):
    def __init__(self, now):
        self.now = now




class TestPlot(unittest.TestCase):
    
    def setUp(self):
        print(self.id())
        
    def assert_im_same(self, name):
        im = imageio.imread(name)
        im_ref = imageio.imread('data/'+name)
        comp = im_ref - im
        self.assertEqual(comp.mean(), 0)
        os.remove(name)
    
    def test_monitor(self):
        s = FakeSim(0)
        m = plot.Monitor(s)
        for (t, y) in EXP_MONITOR:
            s.now = t
            m.observe(y)
        self.assertEqual(m.tseries(), [0] + [t for (t,v) in EXP_MONITOR])
        self.assertEqual(m.yseries(), [0] + [v for (t,v) in EXP_MONITOR])
        self.assertEqual(len(m), len(EXP_MONITOR) + 1)
        self.assertEqual(m.time_average(), 2.15)
        s.now = 20
        self.assertEqual(m.time_average(), (21.5 + 50.) / 20.)
    
    def test_plot_exceptions(self):
        model = get_model()
        model.modules['holder1'].monitor = None
        chart = plot.HolderChart()
        self.assertRaises(Exception, chart.add_serie, 'holder1', model.modules['holder1'])
    
    def test_plot_results(self):
        model = get_model()
        model.emulate(until = EMULATE_UNTIL)
        result = [(pid, 
               p.shape_history, 
               p.space_history, 
               p.create_time, 
               p.dispose_time) for (pid, p) in model.products.items()]
        self.assertEqual(result, EXP_RESULT)
        #print(result)
        chart = plot.HolderChart()
        chart.add_serie('holder1', model.modules['holder1'])
        chart.save('plot_holder1.png')
        self.assert_im_same('plot_holder1.png')
        self.assertEqual(model.modules['holder1'].monitor.time_average(), 2.6)
        self.assertEqual(chart.max, 5)

        
        chart = plot.ProductChart()
        for (pid, p) in model.products.items():
            chart.add_serie(pid, p)
        chart.save('plot_prod1.png')
        self.assert_im_same('plot_prod1.png')
        
        
    def test_plot_product(self):
        import test_sim7 as sim7
        model = sim7.get_model()
        model.emulate(until=sim7.EMULATE_UNTIL)
        chart = plot.ProductChart()
        for (pid, p) in model.products.items():
            chart.add_serie(pid, p)
        chart.save('plot_prod2.png')
        self.assert_im_same('plot_prod2.png')
        
        leg = plot.Legend(chart.legend)
        leg.save('plot_leg1.png')
        self.assert_im_same('plot_leg1.png')
        
        chart = plot.GanttChart()
        chart.add_serie('machine', model.modules['machine'])
        chart.add_serie('transporter', model.modules['transporter'])
        chart.save('plot_gantt1.png')
        self.assert_im_same('plot_gantt1.png')

if __name__ == '__main__':    
    unittest.main()

