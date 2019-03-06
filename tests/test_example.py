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

import util
util.set_path()

from emulica.app import AboutEmulicaDialog

import logging
from emulica.core import set_up_logging
set_up_logging(logging.ERROR)

class TestExample(unittest.TestCase):
    def setUp(self):
        print(self.id())
        self.AboutEmulicaDialog_members = [
        'AboutDialog', 'AboutEmulicaDialog', 'LOGGER', 'logging']

    def test_AboutEmulicaDialog_members(self):
        all_members = dir(AboutEmulicaDialog)
        public_members = [x for x in all_members if not x.startswith('_')]
        public_members.sort()
        self.assertEqual(self.AboutEmulicaDialog_members, public_members)

if __name__ == '__main__':    
    unittest.main()
    #print("test example")
