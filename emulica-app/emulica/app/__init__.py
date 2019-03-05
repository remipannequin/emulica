
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GooCanvas', '2.0')


import optparse
from locale import gettext as _
from gi.repository import Gtk
from gi.repository import Gio
from emulica.app import EmulicaWindow
from emulica.core import set_up_logging
from . emulicaconfig import get_version

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
