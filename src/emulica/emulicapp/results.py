#!/usr/bin/env python
# *-* coding: iso-8859-15 *-*

# emulicapp/results.py
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
"""
emulica is a graphical application to emulica, build using GTK. This (sub) module 
contains functions that pertainng to modelling.
"""
import sys, os, logging
from emulica import plot
import pygtk
pygtk.require('2.0')
import gtk, pango, gobject
import dialogs
logger = logging.getLogger('emulica.emulicapp.results')

class EmulicaResults:
    """Graphical application for emulica : Results part
    
    Attributes:
        
        main
        builder
        summary
        legends
        charts
        results_template
    """

    def __init__(self, main_app):
        """Populate the combos with availables results types"""
        self.main = main_app
        self.builder = main_app.builder
        combo = self.builder.get_object('chart_type_combo')
        notebook = self.builder.get_object('results_notebook')
        self.results_template = [( _("Product Chart"), 'ProductChart', 
                                   lambda m: m.products, 
                                   lambda product: True), 
                                 ( _("Gantt Chart"), 'GanttChart', 
                                   lambda m: m.modules, 
                                   lambda module: ('trace' in dir(module) and len(module.trace) > 0)),
                                 ( _("Holder occupation"), 'HolderChart', 
                                   lambda m: m.modules, 
                                   lambda module: 'monitor' in dir(module))]
        self.charts = list()
        if combo.get_model() == None:
            model = gtk.ListStore(str, str, object, object)    
            for row in self.results_template:
                model.append(row)
            combo.set_model(model)
            cell = gtk.CellRendererText()
            combo.pack_start(cell, True)
            combo.add_attribute(cell, 'text', 0)
        
        #add legend dict
        self.legends = dict()
    
    def prepare(self):
        """Create a Summary, make results buttons sensitive..."""
        #make result tab sensitive
        self.builder.get_object('result_tab_label').set_sensitive(True)
        self.builder.get_object('results_menuitem').set_sensitive(True)
        #add a new summary tab
        self.summary = plot.ResultSummary(self.main.model)
        self.add_result_page(self.summary, _("Summary"))
    
    def on_emulation_finish(self, model):
        """Callback activated when emulation finish. use add_idle, because this 
        function is called from another thread."""
        gobject.idle_add(self.prepare)
    
    def on_export_results_menuitem_activate(self, menuitem, data = None):
        """Callback for the export result menuitem."""
        chooser = gtk.FileChooserDialog(_("Export results..."), self.window,
                                        gtk.FILE_CHOOSER_ACTION_SAVE,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                         gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        response = chooser.run()
        if response == gtk.RESPONSE_OK: 
            raise NotImplemented()
        chooser.destroy()

    def on_result_add_activate(self, widget, data = None):
        """Callback for the add button in the result menu. Display a dialog to
        let the user choose the new graph he want to add"""
        dialog = gtk.Dialog("Add a Result Chart",
                            self.main.window,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                             gtk.STOCK_ADD, gtk.RESPONSE_ACCEPT))
        
        combo = gtk.ComboBox()
        model = gtk.ListStore(str, str, object, object)    
        for row in self.results_template:
            model.append(row)
        combo.set_model(model)
        cell = gtk.CellRendererText()
        combo.pack_start(cell, True)
        combo.add_attribute(cell, 'text', 0)
        all_mod_cb = gtk.CheckButton(label = _("Include all"))
        all_mod_cb.set_active(True)
        hbox = gtk.HBox()
        label = gtk.Label(_("Type of chart"))
        label.set_alignment(1, 0.5)
        label.set_padding(8, 0)
        hbox.pack_start(label)
        hbox.pack_start(combo)
        dialog.vbox.pack_start(hbox)
        dialog.vbox.pack_start(all_mod_cb)
        dialog.show_all()
        if (dialog.run() == gtk.RESPONSE_ACCEPT):
            (chart_name, chart_type, elt, elt_filter) = combo.get_model().get(combo.get_active_iter(), 0, 1, 2, 3)
            self.add_result(chart_name, chart_type, elt, elt_filter, all_mod_cb.get_active())
            
        dialog.destroy()
        
    def on_result_clear_activate(self, widget, data = None):
        """Callback for the clean button in the result menu. Remove any result 
        from the result panel."""
        self.delete_results
        
    def delete_results(self):
        notebook = self.builder.get_object('results_notebook')
        while (notebook.get_n_pages() != 0):
            child = notebook.get_nth_page(-1)
            if (child in self.legends):
                self.legends[child].destroy()
                del self.legends[child]
            notebook.remove_page(-1)
            child.destroy()
        self.charts = list()
        
    def on_result_saveas_activate(self, widget, data = None):
        """Callback for the save button in the result menu. Display a dialog 
        that ask the file name, file format, etc..."""
        dialog = gtk.Dialog("Save Results",
                            self.main.window,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                             gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT))
        hbox1 = gtk.HBox()
        label = gtk.Label(_("Save Results as:"))
        label.set_alignment(0, 0.5)
        label.set_padding(8, 0)
        combo = gtk.combo_box_new_text()
        combo.append_text('pdf')
        combo.append_text('png')
        combo.append_text('eps')
        combo.append_text('jpg')
        combo.append_text('svg')
        combo.set_active(0)
        hbox1.pack_start(label)
        hbox1.pack_start(combo)
        dialog.vbox.pack_start(hbox1)
        cb1 = gtk.CheckButton(_("Include raw result (csv)"))
        cb2 = gtk.CheckButton(_("Include summary (txt)"))
        dialog.vbox.pack_start(cb1)
        dialog.vbox.pack_start(cb2)
        hbox2 = gtk.HBox()
        label2 = gtk.Label(_("File prefix:"))
        label2.set_alignment(0, 0.5)
        label2.set_padding(8, 0)
        entry = gtk.Entry()
        
        base = self.main.filename[:-6]
        entry.set_text(base)
        dir_button = gtk.FileChooserButton(_("Saving Directory"))
        dir_button.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        hbox2.pack_start(label2)
        hbox2.pack_start(entry)
        hbox2.pack_start(dir_button)
        dialog.vbox.pack_start(hbox2)
        dialog.show_all()
        if (dialog.run() == gtk.RESPONSE_ACCEPT):
            #iterate on charts...
            frm = combo.get_active_text()
            for i in range(len(self.charts)):
                ch = self.charts[i]
                ch_name = "{0:s}{1:d}.{2:s}".format(ch.name, i, frm)
                ch_name = os.path.join(dir_button.get_current_folder(), ch_name)
                ch.save(ch_name)
            #save raw results
            if cb1.get_active():
                csv_name = os.path.join(dir_button.get_current_folder(), base+'.csv')
                try:
                    csv = open(csv_name, 'w')
                    for name, module in self.main.model.modules.items():
                        if 'trace' in dir(module):
                            csv.write('Module: {0}\n'.format(name))
                            for (start, end, state) in module.trace:
                                csv.write('{0},\t{1},\t{2}\n'.format(start, end, state))
                            csv.write("\n")
                    #TODO: add products trace in csv
                finally:
                    csv.close()
            if cb2.get_active():
                txt_name = os.path.join(dir_button.get_current_folder(), base+'.txt')
                self.summary.save(txt_name)
        dialog.destroy()

    def on_add_chart_button_clicked(self, button, data = None):
        """Callback connected to the generate gantt chart button. Add a new page in the result notebook"""
        
        combo = self.builder.get_object('chart_type_combo')
        cb = self.builder.get_object('select_chart_all_cb')
        (chart_name, chart_type, elt, elt_filter) = combo.get_model().get(combo.get_active_iter(), 0, 1, 2, 3)
        self.add_result(chart_name, chart_type, elt, elt_filter, cb.get_active())
      
    def on_legend_togglebutton_toggled(self, button, data = None):
        """Callback for the "legend" toggle button"""
        active = button.get_active()
        for legend in self.legends.values():
            #if active, show legend for each results, else, hide...
            if active:
                legend.show()
            else:
                legend.hide()
    
    def add_result(self, chart_name, chart_type, elt, elt_filter, add_all):
        """Add a new result chart.
        
        Arguments:
         chart_name -- the (localized) chart name
         chart_type -- the type of chart to add (the name of a chart constructor
                       (from the plot module)
         elt -- a function that takes the model and output a dictionary of 
                element to chart
         elt_filter -- a function that determine if element should be added or 
                       not to the chart
         add_all -- if true, all elements (modules or product will be added to 
                    the chart
        
        """
        dic = elt(self.main.model)
        chart = getattr(plot, chart_type)()
        if add_all:
            mod_list = [(name, mod) for (name, mod) in dic.items() if elt_filter(mod)]
        else:
            dialog = dialogs.ModuleSelectionDialog(dic, self.main.window, mod_filter = elt_filter)
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_ACCEPT:
                if (chart_type == 'ProductChart'):
                    #for products, key is int(name)
                    mod_list = [(name, dic[int(name)]) for name in dialog.selected()]
                else:
                    #for modules, key is just name...
                    mod_list = [(name, dic[name]) for name in dialog.selected()]
            else:
                mod_list = []
        if len(mod_list) > 0:
            for (name, module) in mod_list:
                chart.add_serie(name, module)
            self.charts.append(chart)
            canvas = chart.create_canvas()
            legend = chart.create_legend(columns = 1)
            self.add_result_page(canvas, chart_name, legend)       
        
    def add_result_page(self, result, name, legend = None):
        """add a new result as a new tab in the results notebook (usuallly 
        called by add_result)"""
        notebook = self.builder.get_object('results_notebook')
        hbox = gtk.HBox()
        hbox.pack_start(result, True, True)
        hbox.show_all()
        if legend:
            sw = gtk.ScrolledWindow()
            sw.add_with_viewport(legend)
            sw.set_policy (hscrollbar_policy=gtk.POLICY_NEVER,
                           vscrollbar_policy=gtk.POLICY_AUTOMATIC)
            self.legends[hbox] = sw
            hbox.pack_start(sw, False, False)
            legend.show()
            active = self.builder.get_object('legend_togglebutton').get_active()
            if active:
                sw.show()
        def on_close_page_button(button, notebook, child):
            if child in self.legends:
                del self.legends[child]
            num = notebook.page_num(child)
            notebook.remove_page(num)
            child.destroy()
        label = gtk.HBox()
        label.pack_start(gtk.Label(name))
        close_page_button = gtk.Button()
        close_page_button.set_relief(gtk.RELIEF_NONE)
        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
        close_page_button.add(img)
        close_page_button.connect('clicked', on_close_page_button, notebook, hbox)
        label.pack_end(close_page_button, False, False)
        label.show_all()
        page_num = notebook.append_page(hbox, tab_label = label)
        notebook.set_current_page(page_num)

