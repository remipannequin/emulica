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

import optparse
from locale import gettext as _
from gi.repository import Gtk # pylint: disable=E0611
from gi.repository import Gio # pylint: disable=E0611
from emulica import EmulicaWindow
from emulica_lib import set_up_logging, get_version

def parse_options():
    """Support for command line options"""
    parser = optparse.OptionParser(version="%%prog %s" % get_version())
    parser.add_option(
        "-v", "--verbose", action="count", dest="verbose",
        help=_("Show debug messages (-vv debugs emulica_lib also)"))
    (options, args) = parser.parse_args()

    set_up_logging(options)

def on_activate(app, data = None):
    window = EmulicaWindow.EmulicaWindow()
    window.show()
    app.add_window(window)
    app.set_menubar = window.get_menubar()
    app_menu = window.get_app_menu()
    if app_menu:
        app.set_app_menu = app_menu

def main():
    'constructor for your class instances'
    parse_options()
    default_settings = Gtk.Settings.get_default();
    default_settings.set_property('gtk-button-images', True); 
    app = Gtk.Application(application_id="net.launchpad.emulica",
                          flags=Gio.ApplicationFlags.FLAGS_NONE)
    app.connect("activate", on_activate)
    app.run(None)
