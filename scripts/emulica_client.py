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

DEFAULT_PORT = 51000
#TODO : migrate file to GTK3...

import sys, logging, zipfile, socket
from gi.repository import Gtk
sys.path.insert(0, '../src')

from emulica import emuML
from emulica.emulation import Report, Request

from twisted.internet import gtk3reactor
gtk3reactor.install()

from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor

class EmulicaLineReceiver(LineReceiver):
    
    delimiter = "\n"
    
    def connectionMade(self):
        self.setLineMode()
        self.factory.update_connection_state(True)
    
    def lineReceived(self, line):
        try:
            rp = emuML.parse_report(line)
            self.factory.addReport(rp)
            if rp.who == 'emulator' and rp.what == 'finished':
                self.transport.loseConnection()
        except emuML.EmuMLError, exp:
            logging.warning(_("Error in processing message: {0}").format(exp))

class EmulicaClient(ClientFactory):
    """This class is a simple emulica client that use gtk..."""
    ClientFactory.protocol = EmulicaLineReceiver

    def __init__(self):
        """Create the client"""
        #ClientFactory.__init__(self)
        self.builder = gtk.Builder()
        self.builder.add_from_file("../ui/emulica_client.ui")
        win = self.builder.get_object('window')
        win.show_all()
        self.builder.connect_signals(self)
        self.connected = False

    def clientConnectionFailed(self, connector, reason):
        print 'connection failed:', reason.getErrorMessage()
        self.add_status("connection failed: {0}".format(reason.getErrorMessage()))
        self.update_connection_state(False)
        #reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print 'connection lost:', reason.getErrorMessage()
        self.add_status("connection lost: {0}".format(reason.getErrorMessage()))
        self.update_connection_state(False)
        #reactor.stop()

    def addReport(self, report):
        #TODO: add report to list, notify
        pass

    def sendRequest(self, request):
        #TODO: add request to list, notify
        line = emuML.write_request(request)
        ClientFactory.protocol.sendLine(line)
        reactor.wakeUp()
        
    def update_connection_state(self, state):
        """Change UI according to the current connection state"""
        #change sensitivity of actions
        for action in map(self.builder.get_object, ['pause_emu', 'start_emu', 'finish_emu', 'add_request']):
            action.set_sensitive(state)
        tb = self.builder.get_object('toggle_connect')
        tb.set_active(state)    
        
    def on_toggle_connect_toggled(self, data = None):
        """Called when the connect/disconnect button is togled"""
        print "toggle connect"
        if self.connected :
            #disconnect
            self.diconnect()
        else:
            self.connect()
        
    def  on_add_request_activate(self, data = None):
        """Called when a request must be created and sent to the emulation server."""
        print "add request"
        
    def on_finish_emu_activate(self, data = None):
        """Called when the user request emulation to finish"""
        self.add_status("ending emulation...")
        self.sendRequest(Request('emulator', 'stop'))
        
    def  on_start_emu_activate(self, data = None):
        """Called when the user request emulation to start"""
        self.add_status("starting emulation...")
        self.sendRequest(Request('emulator', 'start'))
        
    def on_pause_emu_toggled(self, data = None):
        """Called when the user request emulation to pause or resume"""
        print "pause emu"
        
    def on_window_destroy(self, window, data = None):
        """Called when the window is destroyed."""
        reactor.stop()
    
    def add_status(self, message):
        """Push `message` on the status bar"""
        sb = self.builder.get_object('statusbar')
        sb.set_text(message)
        
    def connect(self):
        """Connect to host running emulation server"""
        win = self.builder.get_object('window')
        dialog = gtk.Dialog("Connect to Emulation server", 
                            win, gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                             gtk.STOCK_CONNECT, gtk.RESPONSE_ACCEPT))
        hbox = gtk.HBox()
        label = gtk.Label("Host:")
        entry = gtk.Entry()
        hbox.add(label)
        hbox.add(entry)
        dialog.vbox.add(hbox)
        hbox.show_all()
        
        if dialog.run() == gtk.RESPONSE_ACCEPT:
            addr = entry.get_text()
            addr_components = addr.split(':')
            if len(addr_components) == 1:
                port = DEFAULT_PORT
                host = addr
            elif len(addr_components) == 2:
                host, port = addr_components
            else:
                #error!
                pass
            print "trying to connect..."
            reactor.connectTCP(host, port, self)
        dialog.destroy()
        
    def disconnect(self):
        """Disconnect form emulation server"""
        reactor.disconnect()
    
    def main(self):
        """Main loop method"""
        #gtk.gdk.threads_enter()
        #gtk.main()
        #gtk.gdk.threads_leave()
        reactor.run()
        
        
    
if __name__ == '__main__':
    client = EmulicaClient()
    client.main()
   
