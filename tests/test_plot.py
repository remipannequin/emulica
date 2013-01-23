#! /usr/bin/python
# *-* coding: utf8 *-*

import sys, gtk
sys.path.insert(0, "../src/")
from emulica import plot
import sim4 as sim

def main():
    model = sim.create_model()
    sim.start(model)
    
    win = gtk.Window()
    win.connect("destroy", lambda x: gtk.main_quit())
    win.set_title("Embedding in GTK")
    win.set_size_request(800, 600)
    sw = gtk.ScrolledWindow()
    win.add (sw)
    # A scrolled window border goes outside the scrollbars and viewport
    sw.set_border_width (10)
    # policy: ALWAYS, AUTOMATIC, NEVER
    sw.set_policy (hscrollbar_policy=gtk.POLICY_AUTOMATIC,
                   vscrollbar_policy=gtk.POLICY_AUTOMATIC)

    vbox = gtk.VBox()
    sw.add_with_viewport(vbox)
    
    (g_canvas, l_canvas) = show_product(model)
    g_canvas.set_size_request(800,600)
    vbox.pack_start(g_canvas)
    
    l_win = gtk.Window()
    l_win.connect("destroy", lambda x: gtk.main_quit())
    l_win.set_title("Chart legend")
    l_vbox = gtk.VBox()
    l_win.add (l_vbox)
    l_vbox.pack_start(l_canvas)
    l_win.show_all()
    
    
    (g2_canvas, l2_canvas) = show_gantt(model)
    g2_canvas.set_size_request(800,600)
    vbox.pack_start(g2_canvas)
    
    l2_win = gtk.Window()
    l2_win.connect("destroy", lambda x: gtk.main_quit())
    l2_win.set_title("Chart legend2")
    l2_vbox = gtk.VBox()
    l2_win.add (l2_vbox)
    l2_vbox.pack_start(l2_canvas)
    l2_win.show_all()
    
    canvas = show_queue(model)
    canvas.set_size_request(800,600)
    vbox.pack_start(canvas)
    
    
    
    win.show_all()
    gtk.main()

def show_gantt(model):
    gantt = plot.GanttChart(name = "Sim 7")
    for (name, module) in model.modules.items():
        if 'trace' in dir(module) and not len(module.trace) == 0:
            print "added module %s"%name
            gantt.add_serie(name, module)
    g_canvas = gantt.create_canvas()
    l_canvas = gantt.create_legend(columns = 3)
    return g_canvas, l_canvas

def show_queue(model):
    queue = plot.HolderChart(name = "Sim 7")
    for module in [model.modules[name] for name in ["sink", "source", "espaceMachine"]]:
        queue.add_serie(module.name, module)
    return queue.create_canvas()
    
def show_product(model):
    prod = plot.ProductChart()
    for name, p in model.products.items()[:5]:
        prod.add_serie(name, p)
    g_canvas = prod.create_canvas()
    l_canvas = prod.create_legend(columns = 1)
    return g_canvas, l_canvas
    

if __name__ == '__main__': main()
