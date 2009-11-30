#!/usr/bin/python

import sys
sys.path.insert(0, "../src/")
from emulica import canvas, controler
import sim15
import gtk
import threading, thread

def main():
        ##Not usefull ???
        #gtk.gdk.threads_init() 

        # Open window to hold canvas.
        win = gtk.Window(gtk.WINDOW_TOPLEVEL)
        win.connect('destroy', gtk.main_quit)
        win.set_title('emulica gui')

        # Create VBox to hold canvas and buttons.
        vbox = gtk.VBox()
        win.add(vbox)
        vbox.show()

        vbox.pack_start(canvas)
        canvas.show()

        # Create buttons.
        hbox = gtk.HBox()
        vbox.pack_start(hbox, expand=False)

        b = gtk.Button("Start")
        b.connect("clicked", start)
        hbox.pack_start(b)

        b = gtk.Button("Quit")
        b.connect("clicked", gtk.main_quit)
        hbox.pack_start(b)

        win.show_all()
        gtk.main()

def start(event): 
    emu.start()



if __name__ == '__main__':
    model = sim15.create_model()
    canvas = canvas.EmulicaCanvas(model, None)
##    canvas.apply_layout({'create': (20,100), 
##                         'dispose': (380, 100), 
##                         'cell': (100, 50)})
##    canvas.widgets[model.modules['cell']].module_layer.apply_layout({'cell.machine': (100, 30),
##                                                        'cell.transporter' : (100, 100),
##                                                        'cell.source': (10, 50),
##                                                        'cell.sink': (170, 50)})
    canvas.set_size_request(500, 300)
    emu = controler.TimeControler(model, until = 100, real_time = True, rt_factor = 2)
    
    main()
