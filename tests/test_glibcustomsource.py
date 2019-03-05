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
GLib (event) Source experimentation
"""

import unittest

import util
util.set_path()

from gi.repository import GLib

class MyTestClass:

    i = 0

    def callback(self, data):
        self.i += 1
        #print GLib.get_monotonic_time()
        #print("callback called {times} times".format(times = self.i))
        if self.i == 10:
            #GLib.quit()
            return False
        else:
            return True

class MySource(GLib.Source):
    def __init__(self, callback, inter, mainloop):
        GLib.Source.__init__(self)
        self.callback = callback
        self.interval = inter
        self.mainloop = mainloop
    
    def set_expiration(self, current_time):
        self.expiration = current_time + self.interval*1000
        

    def prepare(self):
        """"""
        #print "calling prepare"
        now = self.get_current_time()
        if now < self.expiration:
            timeout = (self.expiration - now + 999)/1000
            #print "timeout of {0}".format(timeout)
            return (False, timeout)
        else:
            #print "no timeout"
            return (True, 0)

    def check(self):
        #print "calling check"
        now = self.get_current_time()
        r = self.expiration <= now
        #print r
        return True

    def dispatch(self, callback, args):
        #print "calling dispatch"
        r = self.callback(args)
        if not r: 
            self.destroy()
            self.mainloop.quit()
        else:
            self.set_expiration(self.get_current_time())
        return r

class TestGLibCustomEvent(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_1(self):
        #print "create main loop"
        main = GLib.MainLoop()
        #print "create test objects"
        t = MyTestClass()
        source = MySource(t.callback, 1000, main)
        #print "attach"
        source.attach()
        source.set_expiration(source.get_current_time())
        #print "run main loop"
        main.run()
        
    def test_TwoLoops(self):
        #print "create main loop"
        main = GLib.MainLoop()
        #print "create test objects"
        t1 = MyTestClass()
        source1 = MySource(t1.callback, 1000, main)
        
        t2 = MyTestClass()
        source2 = MySource(t2.callback, 2000, main)
        #print "attach"
        source1.attach()
        source2.attach()
        source1.set_expiration(source1.get_current_time())
        source2.set_expiration(source2.get_current_time())
        #print "run main loop"
        main.run()

if __name__ == '__main__':    
    unittest.main()
