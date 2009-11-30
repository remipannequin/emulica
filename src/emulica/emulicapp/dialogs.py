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
emulica is a graphical application to the emulica framework, build using GTK. 
This (sub) module contains functions that pertainng to modelling.
"""
import sys, os, logging, ConfigParser
import gtk, pango, gtksourceview2 as gtksourceview
from emulica import properties 
logger = logging.getLogger('emulica.emulicapp.dialogs')

class ModuleSelectionDialog(gtk.Dialog):
    """This is a custom Dialog that display a list of module to select."""
    def __init__(self, modules, parent = None, title = None, mod_filter = None):
        """Create a new instance.
        
        Arguments:
            modules -- a dictionary of modules to display
            parent -- the parent window (default=None)
            title -- the dialog title
            mod_filter -- a function that determine if a module should be displayed (default=lambda m: True)
        """
        mod_filter = mod_filter or (lambda s: True)
        title = title or _("Select emulation modules to add")
        gtk.Dialog.__init__(self, title,
                            parent,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        
        self.model = gtk.ListStore(bool, str)
        sorted_mod_list = modules.keys()
        sorted_mod_list.sort()
        for name in sorted_mod_list:
            if mod_filter(modules[name]):
                self.model.append((False, name))
        tree = gtk.TreeView(self.model)
        tree.set_property('headers-visible', False)
        #rendering as toggle for col 1
        def toggle(cell, path, model):
            model[path][0] = not model[path][0]
        col_cb_render = gtk.CellRendererToggle()
        col_cb_render.set_property('activatable', True)
        column = gtk.TreeViewColumn(None,  col_cb_render, active = 0)
        column.set_expand(True)
        tree.append_column(column)
        col_cb_render.connect('toggled', toggle, self.model)
        #rendering as text for col 2
        render = gtk.CellRendererText()
        column = gtk.TreeViewColumn(None, render, text = 1)
        column.set_expand(True)
        tree.append_column(column)
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        sw.add(tree)
        
        box = gtk.HBox()
        label = gtk.Label(_("Select:"))
        label.set_padding(8, 0)
        box.pack_start(label)
        bbox = gtk.HButtonBox()
        box.pack_start(bbox)
        select_all = gtk.Button(_("All"))
        select_all.connect('clicked', self.select_all)
        bbox.pack_start(select_all)
        select_none = gtk.Button(_("None"))
        select_none.connect('clicked', self.select_none)
        bbox.pack_start(select_none)
        select_invert = gtk.Button(_("Invert"))
        select_invert.connect('clicked', self.select_invert)
        bbox.pack_start(select_invert)
        
        self.vbox.pack_start(box, False, False)
        self.vbox.pack_start(sw)
        self.show_all()
        
    def selected(self):
        """Return the list of selected modules name"""
        return [name for (checked, name) in self.model if checked]
        
    def select_all(self, button):
        """Select all the rows"""
        for row in self.model:
            row[0] = True
        
    def select_none(self, button):
        """Unselect all the rows"""
        for row in self.model:
            row[0] = False
        
    def select_invert(self, button):
        """Invert selection of the rows"""
        for row in self.model:
            row[0] = not row[0]

class EmulicaPreferences:
    """This class represent the set of preferences for the application. It is 
    based on a ConfigParser.RawConfigParser object."""
    
    def __init__(self, application):
        """Search the preference file and load value form it. If the file is not
        found, use default values."""
        #TODO: Now, there is preference only for the control_view. perhaps more
        #application part later ?
        self.window = application.window
        self.app = application.emulica_control
        self.conf = ConfigParser.RawConfigParser()
        path = self.conf_path()
        res = self.conf.read(self.conf_path())
        if not path in res:
            #the conf file was not read, use defaults values
            self.conf.add_section('control-editor')
            self.conf.set('control-editor', 'show-line-number', 'True')
            self.conf.set('control-editor', 'auto-indent', 'True')
            self.conf.set('control-editor', 'insert-spaces-instead-of-tabs', 'True')
            #self.conf.set('control-editor', 'draw-spaces', 'True')
            self.conf.set('control-editor', 'indent-width', '4')
            self.conf.set('control-editor', 'show-line-marks', 'True') 
    
    def conf_path(self):
        """Return the path of the configuration file."""
        return os.path.join(os.path.expanduser("~"), ".config/emulica/preferences.ini")
    
    def __boolean_edit(self, section, opt_name):
            """Return an entry to edit this option as a boolean."""
            cb = gtk.CheckButton()
            value = self.conf.getboolean(section, opt_name)
            cb.set_active(value)
            def on_toggled(cb, section, opt_name):
                value = cb.get_active()
                self.conf.set(section, opt_name, str(value))
            cb.connect('toggled', on_toggled, section, opt_name)
            return cb
            
    def __integer_edit(self, section, opt_name):
        """Return an entry to edit this option as an integer."""
        value = self.conf.getint(section, opt_name)
        sb = gtk.SpinButton(gtk.Adjustment(value = value, lower = 0, upper = 100, step_incr = 1))
        def on_value_changed(sb, section, opt_name):
            value = sb.get_value()
            self.conf.set(section, opt_name, str(int(value)))
        sb.connect('value-changed', on_value_changed, section, opt_name)
        return sb
                
                
    def edit(self):
        """Display a gtk.Dialog to edit the preferences, and apply the new value
        if the OK button is clicked."""
        dialog = gtk.Dialog(_("Preferences for emulica"), 
                            self.window, gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        
        nb = gtk.Notebook()
        options = self.conf.options('control-editor')
        table = gtk.Table(len(options), 2)
        nb.append_page(table, gtk.Label(_("Control Edition")))
        prefs_edit = {'show-line-number': (_("Show line numbers:"), self.__boolean_edit),
                     'auto-indent': (_("Auto-indent:"), self.__boolean_edit),
                     'insert-spaces-instead-of-tabs': (_("Insert spaces instead of tabs:"), self.__boolean_edit),
                     'indent-width': (_("Indent width:"), self.__integer_edit),
                     'show-line-marks': (_("Show line marks"), self.__boolean_edit)}
        row = 0
        for opt in options:
            (label_string, entry_fn) = prefs_edit[opt]
            label = gtk.Label(label_string)
            label.set_alignment(1, 0.5)
            label.set_padding(8, 0)
            table.attach(label, 0, 1, row, row + 1)
            entry = entry_fn('control-editor', opt)
            table.attach(entry, 1, 2, row, row + 1)
            row += 1
        
        nb.show_all()
        dialog.vbox.pack_start(nb)
        response = dialog.run()
        if response == gtk.RESPONSE_ACCEPT:
            self.apply()
            self.write()
        dialog.destroy()
    
    def apply(self):
        """Apply preferences on the application."""
        ctrl_view = self.app.control_view
        ctrl_view.modify_font(pango.FontDescription('monospace'))
        
        ctrl_view.set_show_line_numbers(self.conf.getboolean('control-editor', 'show-line-number'))
        ctrl_view.set_auto_indent(self.conf.getboolean('control-editor','auto-indent'))
        ctrl_view.set_insert_spaces_instead_of_tabs(self.conf.getboolean('control-editor','insert-spaces-instead-of-tabs'))
        #Work around win32 version
        if 'DRAW_SPACE_SPACE' in dir(gtksourceview):
            ctrl_view.set_property('draw-spaces', gtksourceview.DRAW_SPACES_SPACE)

        ctrl_view.set_indent_width(self.conf.getint('control-editor','indent-width'))
        ctrl_view.set_show_line_marks(self.conf.getboolean('control-editor','show-line-marks'))
    

    def write(self):
        """Write the configuration file."""
        path = self.conf_path()
        if not os.path.exists(path):
            logger.warn("creating a new preference file in {0}".format(path))
            dir = os.path.dirname(path)
            if not os.path.exists(dir):
                os.makedirs(dir)
        with open(self.conf_path(), 'w') as f:
            self.conf.write(f)
            
class EmulicaExecSettings(gtk.Dialog):
    """A dialog that enable editing execution settings """
        
    def __init__(self, window, props):
        """Create the new dialog, populate and show it."""
        gtk.Dialog.__init__(self, _("Execution settings"), 
                            window, gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        
        table = gtk.Table(4, 2)
        labels = dict()
        for (text, row) in [(_("Time advance mode:"),0), 
                            (_("Time limit:"), 1),
                            (_("Real-time factor:"), 2),
                            (_("Animate emulation:"), 3)]:
            labels[row] = gtk.Label(text+"  ")
            labels[row].set_alignment(1, 0.5)
            table.attach(labels[row], 0, 1, row, row + 1)
        self.combo = gtk.combo_box_new_text()
        modes = [_("Discrete events"), _("Real-time")]
        for text in modes:
            self.combo.append_text(text)        
        self.combo.set_active(props['exec']['real-time'])
        table.attach(self.combo, 1, 2, 0, 1)
        self.limit_adj = gtk.Adjustment(value=props['exec']['limit'], 
                                        lower=0, 
                                        upper=10000000, 
                                        step_incr=1, 
                                        page_incr=10)
        table.attach(gtk.SpinButton(self.limit_adj), 1, 2, 1, 2)
        self.rt_factor_adj = gtk.Adjustment(value=props['exec']['rt-factor'], 
                                            lower=1,
                                           upper=50,
                                           step_incr=1, 
                                           page_incr=2)
        self.rt_spin = gtk.SpinButton(self.rt_factor_adj)
        table.attach(self.rt_spin, 1, 2, 2, 3)
        self.animate_cb = gtk.CheckButton()
        self.animate_cb.set_active(props['exec']['animate'])
        table.attach(self.animate_cb, 1, 2, 3, 4)
        
        def combo_value_changed(combo):
            if combo.get_active() == 0:
                self.rt_spin.set_sensitive(False)
                labels[2].set_sensitive(False)
            else:
                self.rt_spin.set_sensitive(True)
                labels[2].set_sensitive(True)
        combo_value_changed(self.combo)
        self.combo.connect("changed", combo_value_changed)
        self.vbox.add(table)
        self.show_all()
            
    def get_rt(self):
        return (self.combo.get_active() == 1)
        
    def get_limit(self):
        return self.limit_adj.get_value()
        
    def get_rt_factor(self):
        return self.rt_factor_adj.get_value()
        
    def get_animate(self):
        return self.animate_cb.get_active()
    
            
class EmulicaAbout(gtk.AboutDialog):
    
    
    def __init__(self, window):
        """Create and show the about dialog."""
        authors = ['Rémi Pannequin <remi.pannequin@cran.uhp-nancy.fr>']
        gtk.AboutDialog.__init__(self)
        self.set_transient_for(window)
        self.set_destroy_with_parent(True)
        self.set_name(_("Emulica"))
        self.set_version('0.6')
        self.set_copyright('Copyright \xc2\xa9 2008, 2009 Rémi Pannequin, Centre de Recherche en Automatique de Nancy')
        self.set_website('http://emulica.sourceforge.net')
        self.set_comments(_("Interface to emulica, a emulation modelling and execution environment."))
        self.set_authors            (authors)
        self.set_logo_icon_name     ('emulica-icon')
        self.connect('response', self.close)
        self.connect('delete-event', self.delete_event)
        self.show()
            
    def close(self, dialog, response):
        """Callbacks for destroying the dialog"""
        self.hide()
        
    def delete_event(self, dialog, event):
        """Callbacks for destroying the dialog"""
        return True
            
class EmulicaStatusBar:
    """The status bar.
    
    Attributes:
        statusbar
        cid
        progressbar
        
    """    
    
    def __init__(self, main):
        """Get the statusbar from the main app. Add a combo for selecting exec mode and a progress bar"""
        self.statusbar = main.builder.get_object('statusbar')
        self.cid = self.statusbar.get_context_id('SEME')
        self.progressbar = gtk.ProgressBar()
        self.statusbar.pack_end(self.progressbar)
        
    def reset(self, filename):
        """Reset the status bar and changed flag"""
        if filename: status = _("File: {0}").format(os.path.basename(filename))
        else: status = _("File: (UNTITLED)")
        self.statusbar.push(self.cid, status)
    
    def set_text(self, message):
        """Push message on statusbar"""
        self.statusbar.push(self.cid, message)
        
    def set_progress(self, state, current = 0, limit = 1):
        """Set the progressbar label and fraction"""
        self.progressbar.set_fraction(current / limit)
        self.progressbar.set_text("{0}, t={1:.1f}".format(state, current))
        
    def set_progressing(self, state):
        """Set the progress bar to the moving-bar style: used in discrete event simulation."""
        #TODO: repeditively call pulse
        self.progressbar.pulse()
        
        
        
class ModelPropertiesDialog(gtk.Dialog):
    """A dialog that enable to add, remove and edit properties of a model."""
    
    
                  
    
    def __init__(self, window, model, command_manager):
        """Create the dialog, populate and show it."""
        gtk.Dialog.__init__(self, _("Model input interface"), 
                            window, gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_ADD, gtk.RESPONSE_ACCEPT,
                            gtk.STOCK_REMOVE, gtk.RESPONSE_REJECT,
                            gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.model = model
        self.inputs = model.inputs
        self.properties = self.model.properties
        
        #create a treeview
        treeview = self.__create_treeview()
        #create a SW, put the treeview into it, add it to the vbox
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(treeview)
        self.vbox.pack_start(sw)
        treeview.connect('cursor_changed', self.on_treeview_cursor_changed, treeview.get_selection())
        treeview.connect('key-press-event', self.on_key_press_event, treeview.get_selection())
        self.connect('response', self.response, treeview.get_selection())
        self.connect('delete-event', self.delete_event)
        self.show_all()
        
    def response(self, dialog, response, selection):
        """Response callbacks"""
        if response == gtk.RESPONSE_ACCEPT:
            #add a new row
            self.__add_row()
        elif response == gtk.RESPONSE_REJECT:
            #del selected rows
            self.__del_row(selection)
        else:
            #close dialog:
            self.destroy()
        
    def delete_event(self, dialog, event):
        """Callbacks for destroying the dialog"""
        return True
        
    def __create_treeview(self):
        self.tree_model = gtk.ListStore(str, str, str)
        for (name, (module, prop)) in self.inputs.items():
            self.tree_model.append([name, module, prop])
        treeview = gtk.TreeView(self.tree_model)
        #rendering column 1 as text Entry
        col_name_render = gtk.CellRendererText()
        col_name_render.set_property('editable', True)
        column = gtk.TreeViewColumn('Input Name', col_name_render, text = 0)
        column.set_expand(True)
        treeview.append_column(column)
        col_name_render.connect('edited', self.apply_change_name)
        
        #rendering col 2 as combo
        col_mod_render = gtk.CellRendererCombo()
        col_mod_render.set_property('editable', True)
        self.mod_list = gtk.ListStore(str, object)
        for mod in self.model.module_list():
            self.mod_list.append([mod.name, mod])
        col_mod_render.set_property('model', self.mod_list)
        col_mod_render.set_property('text_column', 0)
        column = gtk.TreeViewColumn('Module', col_mod_render, text = 1)
        column.set_expand(True)
        treeview.append_column(column)
        col_mod_render.connect('changed', self.on_combomod_changed)
        
        
        #rendering col 3 as combo
        col_prop_render = gtk.CellRendererCombo()
        col_prop_render.set_property('editable', True)
        self.prop_list = gtk.ListStore(str)
        col_prop_render.set_property('model', self.prop_list)
        col_prop_render.set_property('text_column', 0)
        column = gtk.TreeViewColumn('Property', col_prop_render, text = 2)
        column.set_expand(True)
        treeview.append_column(column)
        col_prop_render.connect('changed', self.on_comboprop_changed)
        return treeview
    
        
    def __add_row(self):
        row = self.tree_model.append()
        prop_name = _("property{0}").format(self.tree_model.get_string_from_iter(row))
        self.tree_model.set(row, 0, prop_name)
        self.tree_model.set(row, 1, self.mod_list[0][0])
        self.update_prop_list(row)
        self.tree_model.set(row, 2, self.prop_list[0][0])
        self.update_inputs(row)

    def __del_row(self, selection):
        #code adapted from pygtk faq
        model, treeiter, = selection.get_selected()
        if treeiter:
            path = model.get_path(treeiter)
            (prop, ) = self.tree_model.get(treeiter, 0)
            del self.inputs[prop]
            model.remove(treeiter)
            selection.select_path(path)    
            if not selection.path_is_selected(path):
                row = path[0]-1
                if row >= 0:
                    selection.select_path((row,))


    def update_inputs(self, treeiter):
        name, = self.tree_model.get(treeiter, 0)
        mod_name, = self.tree_model.get(treeiter, 1)
        prop_name, = self.tree_model.get(treeiter, 2)
        self.inputs[name] = (mod_name, prop_name)

        
    def update_prop_list(self, treeiter):
        (name, ) = self.tree_model.get(treeiter, 0)
        (mod_name, ) = self.tree_model.get(treeiter, 1)
        module = self.model.get_module(mod_name)
        #update prop_list
        self.prop_list.clear()
        for p_name in module.properties.keys():
            self.prop_list.append([p_name])

    def on_combomod_changed(self, combo, path, selected_iter):
        """Clear and populate self.prop_list. Add/change values in inputs"""
        #get iter on selected row in tree
        treeiter = self.tree_model.get_iter_from_string(path)
        #get the new module and name
        (name, mod) = self.mod_list[selected_iter]
        self.update_prop_list(treeiter)
        self.tree_model.set(treeiter, 1, name)
        self.tree_model.set(treeiter, 2, self.prop_list[0][0])
        self.update_inputs(treeiter)
        
        
    def on_comboprop_changed(self, combo, path, selected_iter):
        """Add/change values in inputs"""
        name =  self.prop_list[selected_iter][0]
        treeiter = self.tree_model.get_iter_from_string(path)
        self.tree_model.set(treeiter, 2, name)
        self.update_inputs(treeiter)
        
    def on_new_button_clicked(self, button):
        """Callback connected to 'New' button. Add a new row on double click."""
        self.__add_row()
    
    def on_del_button_clicked(self, button, selection):
        """Callback connected to 'Delete' button. Delete selected row on Del key."""
        self.__del_row(selection)

    def on_key_press_event(self, widget, event, selection = None):
        """Callback connected to button-clicks. Delete selected row on Del key."""
        if event.type == gtk.gdk.KEY_PRESS and 'Delete' == gtk.gdk.keyval_name(event.keyval):
            self.__del_row(selection)
    
    def on_treeview_cursor_changed(self, treeview, selection):
        """Called when the cursor position change in the treeview; Get selected 
        row, and display corresponding program's properties."""
        model, treeiter, = selection.get_selected()
        if treeiter:
            self.update_prop_list(treeiter)
            
    
    def apply_change_name(self, cellrenderertext, path, new_name):
        """Change property name"""
        treeiter = self.tree_model.get_iter_from_string(path)
        old_name, = self.tree_model.get(treeiter, 0)
        self.tree_model.set(treeiter, 0, new_name)
        value = self.inputs[old_name]
        del self.inputs[old_name]
        self.inputs[new_name] = value

            
    
