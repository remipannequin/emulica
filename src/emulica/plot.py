#! /usr/bin/python
# *-* coding: iso-8859-15 *-*

# plot.py
# Copyright 2008, Rémi Pannequin, Centre de Recherche en Automatique de Nancy
# 
# This file is part of Emulica.
#
# Emulica is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Emulica is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Emulica.  If not, see <http://www.gnu.org/licenses/>.

"""This module allow to create various charts from emulica results."""

import logging, gtk, goocanvas
from matplotlib import figure, patches, colors, cm
from matplotlib.backends.backend_gtkagg import FigureCanvasGTKAgg as FigureCanvas

logger = logging.getLogger('emulica.plot')

class ResultSummary(gtk.Table):
    
    def __init__(self, model):
        gtk.Table.__init__(self, 16, 3)
        entries = []
        self.avg_occupation = dict()
        self.avg_lifetime = dict()
        self.avg_utilization = dict()
        self.physical_prop = dict()

        self.categs = [(_("General"), 0),
                       (_("Actuators"), 7),
                       (_("Products"), 10),
                       (_("Holders"), 14)]
        for (string, row) in self.categs:
            label = gtk.Label()
            label.set_markup('<b><big>{0}</big></b>'.format(string))
            self.attach(label, 0, 2, row, row + 1)
        
        separators = [6, 9, 13]
        for row in separators:
            self.attach(gtk.HSeparator(), 1, 3, row, row + 1)
        
        self.labels = [(_("Number of products:"), 1),
                       (_("Simulation length:"), 2),
                       (_("Average actuator utilization:"), 3),
                       (_("Average product lifetime:"), 4),
                       (_("Average holder occupation:"), 5),
                       (_("Utilization:"), 8),
                       (_("Lifetime:"), 11),
                       (_("Occupation:"),15)]
        for (string, row) in self.labels:
            label = gtk.Label(string)
            label.set_padding(10, 0)
            label.set_alignment(1, 0.5)
            self.attach(label, 1, 2, row, row + 1, yoptions = gtk.FILL)
            entry = gtk.Entry()
            entry.set_property('editable', False)
            entries.append(entry)
            self.attach(entry, 2, 3, row, row + 1, yoptions = gtk.FILL)
        
        #create a treeview for product's physical props
        label = gtk.Label(_("Physical attributes:"))
        label.set_alignment(1, 0.1)
        label.set_padding(10, 0)
        self.attach(label, 1, 2, 12, 13, yoptions = gtk.EXPAND|gtk.FILL)
        self.phys_prop_model = gtk.ListStore(str, str)
        phys_prop_tv = gtk.TreeView(self.phys_prop_model)
        phys_prop_tv.set_size_request(-1, 50)
        col_render = gtk.CellRendererText()
        col_render.set_property('editable', False)
        phys_prop_tv.append_column(gtk.TreeViewColumn('Name', col_render, text = 0))
        phys_prop_tv.append_column(gtk.TreeViewColumn('Value', col_render, text = 1))
        phys_prop_tv.set_property('headers-visible', False)
        phys_prop_tv.set_property('rules-hint', True)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(phys_prop_tv)
        frame = gtk.Frame()
        frame.add(sw)
        self.attach(frame, 2, 3, 12, 13, yoptions = gtk.EXPAND|gtk.FILL)
        
        #create the combo
        combo = gtk.combo_box_new_text()
        for (name, module) in model.modules.items():
            if 'trace' in dir(module):
                combo.append_text(name)
                if (model.current_time() == 0):
                    self.avg_utilization[name] = 0
                else:
                    self.avg_utilization[name] = float(sum([tr[1] - tr[0] for tr in module.trace if not tr[2] in ['setup', 'failed']]) / model.current_time())
        combo.connect("changed", self.on_report_actuators_change, entries)
        self.attach(combo, 2, 3, 7, 8)
        
        combo = gtk.combo_box_new_text()
        for (name, product) in model.products.items():
            combo.append_text(str(name))
            self.avg_lifetime[str(name)] = float(product.dispose_time - product.create_time)
            self.physical_prop[str(name)] = product.properties
        combo.connect("changed", self.on_report_product_change, entries)
        self.attach(combo, 2, 3, 10, 11)
        
        combo = gtk.combo_box_new_text()
        for (name, module) in model.modules.items():
            if 'monitor' in dir(module):
                combo.append_text(name)
                self.avg_occupation[name] = module.monitor.timeAverage() or float(0)
        combo.connect("changed", self.on_report_holder_change, entries)
        self.attach(combo, 2, 3, 14, 15)
        
        def avg(dic):
            if (len(dic)==0): 
                return 0
            else: 
                return sum(dic.values()) / len(dic)
        
        self.general = [len(model.products), 
                        model.current_time(), 
                        avg(self.avg_utilization), 
                        avg(self.avg_lifetime),
                        avg(self.avg_occupation)]
        
        
        entries[0].set_text('{0:n}'.format(self.general[0]))
        entries[1].set_text('{0:.2f}'.format(self.general[1]))
        entries[2].set_text('{0:.2%}'.format(self.general[2]))
        entries[3].set_text('{0:.2f}'.format(self.general[3]))
        entries[4].set_text('{0:.2f}'.format(self.general[4]))
        
    def on_report_actuators_change(self, combo, entries):
        """Callback for the actuator selection combo. display key value in the 
        report summary panel.
        """
        name = combo.get_active_text()
        entries[5].set_text('{0:.2%}'.format(self.avg_utilization[name]))

    def on_report_product_change(self, combo, entries):
        """Callback for the product selection combo. display key value in the 
        report summary panel.
        """
        name = combo.get_active_text()
        entries[6].set_text('{0:.2f}'.format(self.avg_lifetime[name]))
        #TODO: display physical properties as multi-line entry
        self.phys_prop_model.clear()
        for (name, value) in self.physical_prop[name].items():
            self.phys_prop_model.append((name, value))
        
        
    def on_report_holder_change(self, combo, entries):
        """Callback for the holder selection combo. display key value in the 
        report summary panel.
        """
        name = combo.get_active_text()
        entries[7].set_text('{0:.2f}'.format(self.avg_occupation[name]))
        
    def save(self, filename):
        """Save the summary in a file."""
        try:
            f = open(filename, 'w')
            #call repr
            f.write(str(self))
        finally:
            f.close()

    def __repr__(self):
        """Display the summary"""
        s = str()
        s += '=========={0}==========\n'.format(self.categs[0][0])
        for i in range(5):
            s += '{0}\t\t{1}\n'.format(self.labels[i+1][0], self.general[i])
        #actuators
        s += '\n=========={0}==========\n'.format(self.categs[1][0])
        s += _("Name:")+"\t\t"+self.labels[5][0]+'\n'
        for name, value in self.avg_utilization.items():
            s += '{0}\t\t{1}\n'.format(name, value)
        #products
        s += '\n=========={0}==========\n'.format(self.categs[2][0])
        s += _("ProdID:")+"\t\t"+self.labels[6][0]+'\n'
        for name, value in self.avg_lifetime.items():
            s += '{0}\t\t{1}\n'.format(name, value)
        #holders
        s += '\n=========={0}==========\n'.format(self.categs[3][0])
        s += _("Name:")+"\t\t"+self.labels[7][0]+'\n'
        for name, value in self.avg_occupation.items():
            s += '{0}\t\t{1}\n'.format(name, value)
        return s
        

class HolderChart:
    """A graph that show holders occupation as a function of time. several 
    Holder can be displayed on the same graph
    """

    def __init__(self, name = "holder occupation"):
        """Create a new instance of this graph"""
        self.name = name
        self.__fig = figure.Figure()
        self.__fig.hold(False)
        self.plot = self.__fig.add_subplot(111)
        self.lines = []
        self.labels = []
        self.legend = dict()
        self.max = 0
    
    def process_trace(self, t, s):
        """Make data suitable for a "step" plot."""
        res_s = []
        res_t = []
        i = 0
        for i in range(len(t)-1):
            res_s.append(s[i])
            res_t.append(t[i])
            res_s.append(s[i])
            res_t.append(t[i+1])
            self.max = max(self.max,s[i])    
        res_s.append(s[i])
        res_t.append(t[i])
        res_s.append(s[i])
        res_t.append(t[i]+1)
        self.max = max(self.max,s[i])
        return (res_t, res_s)
    
    def add_serie(self, name, holder):
        """Add a line in the graph."""
        monitor = holder.monitor
        #check whether there is actually some traces in the monitor
        if not len(monitor) == 0:
            t = monitor.tseries()
            s = monitor.yseries()
        else:
            t = [0]
            s = [0]
        (t, s) = self.process_trace(t, s)
        self.plot.set_ylabel(name)
        line = self.plot.plot(t, s, linewidth=1.0)
        converter = colors.ColorConverter()
        self.legend[name] = converter.to_rgba(line[0].get_color())
        
    def __finish_plot(self):
        """Finish drawing the plot and set mics options."""
        self.plot.set_xlabel(_("time"))
        self.plot.set_ylabel(_("holder occupation"))
        self.plot.set_title(self.name)
        self.plot.grid(True)
        self.plot.set_ylim(0, self.max + 1)
        
    def create_canvas(self):
        """Return a cairo embeddable widget."""
        self.__finish_plot()
        canvas = FigureCanvas(self.__fig)
        canvas.set_size_request(-1, 200)
        return canvas
        
    def create_legend(self, columns = 2):
        """Return the widget for the chart's legend."""
        #TODO: remove the graph's legend and create a new one (using lines instead of rects)
        return Legend(self.legend, columns)

    def save(self, filename):
        """save the chart in a file"""
        self.__fig.savefig(filename, dpi = 100)

class ProductChart:
    """
    A gantt chart that focus on products
    """
    def __init__(self, name = _("product life-cycle"), limit = 50):
        """Create a new instance of a ProductChart"""
        self.name = name
        self.limit = limit
        self.__fig = figure.Figure()
        self.plot = self.__fig.add_subplot(111)
        self.rows = []
        self.legend = dict()
        self.colormap = cm.ScalarMappable(cmap = cm.gist_rainbow)
        self.colormap.set_clim(0, 1)
    
    def add_serie(self, name, prod):
        """Add data correponding to a new product. Basicaly, it is adding a line
        in a gantt chart, with its PID as title. Create and Dispose time are marked as
        tick vertical line."""
        if len(self.rows) > self.limit:
            logger.warning(_("Too many row in product chart, add_serie is ignored..."))
            return
        space_tr = []
        i = -1
        for i in range(len(prod.space_history) - 1):
            space_tr.append((prod.space_history[i][0], prod.space_history[i+1][0] - prod.space_history[i][0]))
            space = prod.space_history[i][1]
            if not space in self.legend:
                self.legend[space] = color_from_int(self.colormap, len(self.legend) + 1)
        
        i += 1
        space_tr.append((prod.space_history[i][0], prod.dispose_time - prod.space_history[i][0]))
        space = prod.space_history[i][1]
        if not space in self.legend:
            self.legend[space] = color_from_int(self.colormap, len(self.legend) + 1)
        y = len(self.rows) + 0.35
        self.plot.broken_barh(space_tr, (y, 0.3), facecolors = [self.legend[s[1]] for s in prod.space_history])
        
        #draw line and annotations for
        for shape_tr in prod.shape_history:
            self.plot.hlines([y + 0.35] ,[shape_tr[0]], [shape_tr[1]], lw=3)
            self.plot.text(shape_tr[0], y + 0.37, "{0}, {1}".format(shape_tr[2], shape_tr[3]))
        
        #draw lines for create time and dispose time
        self.plot.vlines([prod.create_time, prod.dispose_time], [y], [y+0.5], lw=3)
        
        
        self.rows.append(prod.pid)          
                                  
    def __create_plot(self):
        """Create actual plot"""
        
        self.plot.set_ylim(0, len(self.rows))
        self.plot.set_xlabel('time')
        self.plot.set_yticks([i+0.5 for i in range(len(self.rows))])
        self.plot.set_yticklabels(self.rows)
        self.plot.set_yticklabels(self.rows)
        self.plot.grid(True)
        
    def save(self, filename):
        """save the chart in a file"""
        self.__fig.savefig(filename, dpi = 100)
    
    def create_canvas(self):
        """Return a cairo embeddable widget"""
        self.__create_plot()
        canvas = FigureCanvas(self.__fig)
        return canvas

    def create_legend(self, columns = 2):
        """Return the widget for the chart's legend."""
        return Legend(self.legend, columns)

class GanttChart():
    """
    A Gantt chart showing colored horital bar to show activity of resources...
    
    Attributes:
        name -- the name of the graph
        plot -- the chart's plot
        
    """
    def __init__(self,name = _("gantt chart")):
        """Create a new instance of a GanttChart
        
        Arguments:
            name -- The name of the chart (default="gantt chart")
            legend -- a dictionary of the form (entry: color_name)
        """
        
        self.name = name
        self.__fig = figure.Figure()
        self.__fig.hold(False)
        self.plot = self.__fig.add_subplot(111)
        self.rows = []
        self.legend = {'setup': (0.4, 0.4, 0.4, 1), 'failure': (0, 0, 0, 0.5)}
        self.colormap = cm.ScalarMappable(cmap = cm.jet)
        self.colormap.set_clim(0, 1)
    
    def process_trace(self, trace):
        """Return a condensed trace"""
        failures = list()
        
                
        
        condensed = list()
        epsilon = pow(10,-6)
        if not len(trace) == 0:
            #remove failures from the list
            for tr in trace:
                p = tr[2]
                if p == 'failure':
                    failures.append(tr)
            for tr in failures:
                trace.remove(tr)
            #condensate the rest
            p = trace[0][2]
            start = trace[0][0]
            end = trace[0][1]
            for tr in trace[1:]:
                if tr[0] == tr[1]:
                    pass
                elif tr[2] == p and abs(tr[0] - end) < (end * epsilon):
                    end = tr[1]
                else: 
                    condensed.append((start, end, p))
                    start = tr[0]
                    p = tr[2]
                    end = tr[1]
            condensed.append((float(start), float(end), p))
            
            #add legend entries
            for (start, end, p) in condensed:
                if not p in self.legend.keys():
                    self.legend[p] = color_from_int(self.colormap, len(self.legend))
        else:
            condensed.append((0, 0, 'failure'))
            logger.warning(_("Adding an empty trace to gantt chart"))
        return (condensed, failures)
    
    def add_serie(self, name, module):
        """Add a new resource trace (i.e. a new line) to the gantt chart. The 
        module object must have a trace attribute that is a list of tuples of 
        the form: (start, end, state)
        
        Arguments:
            name -- the name of the resource
            module -- the module 
        """
        trace = module.trace
        #condensate the trace
        (condensed, failures) = self.process_trace(trace)
        #add to plot
        y = 10*(len(self.rows)+1)
        self.plot.broken_barh([(tr[0], tr[1] - tr[0]) for tr in condensed], 
                              (y, 9),
                              color = [self.legend[tr[2]] for tr in condensed])
        self.plot.broken_barh([(tr[0], tr[1] - tr[0]) for tr in failures], 
                              (y, 3),
                              color = 'black')
        self.plot.broken_barh([(tr[0], tr[1] - tr[0]) for tr in failures], 
                              (y+6, 3),
                              color = 'black')                      
        self.rows.append(name)
        
    def __create_plot(self):
        """Create actual plot"""
        i = len(self.rows)
        self.plot.set_ylim(5,(i * 10) + 15)
        self.plot.set_xlabel('time')
        self.plot.set_yticks([(y + 1) * 10 + 5 for y in range(i)])
        self.plot.set_yticklabels(self.rows)
        self.plot.grid(True)
        
    def save(self, filename):
        """Save the chart in a file"""
        self.__create_plot()
        self.__fig.savefig(filename, dpi = 100)
    
    def create_canvas(self):
        """Return a cairo embeddable widget"""
        self.__create_plot()
        canvas = FigureCanvas(self.__fig)
        canvas.set_size_request(-1, 100 + 30 * len(self.rows))
        return canvas

    def create_legend(self, columns = 2):
        """Return the widget for the chart's legend."""
        return Legend(self.legend, columns)
        
        

class Legend(goocanvas.Canvas):
    """This class can be used to draw a legend for a chart. It is based on a 
    goocanvas.Canvas that contains color rectangles (or lines) associated a 
    color with a string. Entries are sorted in alphabetical order"""
    
    def __init__(self, data, columns):
        """Create a new instance of a Legend. 
        
        Arguments:
            data --  a dictionary in which each item represent a legend item.
                     the keys are the legend strings, and value must be 
                     gtk.gdk.Colors
            column -- the number of column to use to format the table 
        """
        def ceil(a, b):
            """Return the number of row required to pack a values in b columns"""
            q, r = divmod(a, b)
            if r: return q+1
            else: return q
        goocanvas.Canvas.__init__(self)
        self.set_size_request(100, 500)
        self.table = goocanvas.Table(parent = self.get_root_item(),
                                     homogeneous_columns = True,
                                     homogeneous_rows = True)
        entries = data.keys()
        entries.sort()
        sorted_data = [(entry, data[entry]) for entry in entries]
        i = 0
        for (legend_string, legend_color) in sorted_data:
            col = i % columns
            row = i // columns
            item = self._legend_entry(legend_string, legend_color)
            self.table.set_child_properties(item, 
                                            row = row, 
                                            column = col,
                                            x_align = 0,
                                            x_expand = True,
                                            x_fill = True,
                                            x_shrink = True,
                                            y_expand = True,
                                            y_fill = True,
                                            y_shrink = True,
                                            right_padding = 20)
            i += 1
        b = self.table.get_bounds()
        self.set_size_request(int(b.x2), int(b.y2))    
        
    def _legend_entry(self, string, color):
        """Return a new goocanvas Item that represents a legend item."""
        rgb = [int(c*65535) for c in color[:3]]
        color = gtk.gdk.Color(*rgb)
        item = goocanvas.Table(parent = self.table)
        rect = goocanvas.Rect(parent = item,
                              x = 0,
                              y = 0,
                              width = 25,
                              height = 25,
                              line_width = 1,
                              stroke_color = 'black',
                              fill_color = color.to_string())
        if string == 'failure':
            rect = goocanvas.Rect(parent = item,
                              x = 0,
                              y = 8,
                              width = 25,
                              height = 8,
                              line_width = 1,
                              stroke_color = 'black',
                              fill_color = 'white')
        item.set_child_properties(rect, column = 0, left_padding = 10, 
                                  top_padding = 10, bottom_padding = 10,
                                  right_padding = 10)
        text = goocanvas.Text(parent = item,
                              text = string,
                              x = 0,
                              y = 0,
                              anchor = gtk.ANCHOR_W,
                              font = 'arial')
        item.set_child_properties(text, column = 1)
        return item
        
        
        
    

def color_from_int(colormap, n):
    """Return a color in the colormap the correspond to the integer n (greater than zero).
    it return the following sequence: 1, 1/2, 1/4, 3/4, 1/16, 3/16, 5/16, ...
    """
    assert n > 0
    from math import log, floor
    p = floor(log(n, 2))
    s = (2 * (n - pow(2, p)) + 1)/(pow(2, p + 1))
    
    return colormap.to_rgba(s)
    
