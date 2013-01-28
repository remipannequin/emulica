#!/usr/bin/env python
# *-* coding: iso-8859-15 *-*

# emulicapp/__init__.py
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
emulicapp is a graphical application to the emulica framework, build using GTK.
"""

import sys, os, pickle, zipfile, random, logging
from emulica import emuML, controler, emulation
import pygtk
pygtk.require('2.0')
import gtk, gobject
import dialogs, modelling, control, results

application = 'emulica'
import gettext
gettext.install(application)

logger = logging.getLogger('emulica.emulicapp')    

class Emulica:
    """Graphical application for emulica
    
    Attributes:
        window -- the main window
        builder -- GtkBuilder object
        context_menu -- the context menu
        
        emulica_model
        emulica_control
        emulica_results
        
    """
    def __init__(self, ui_path, icon_path= '/usr/share/emulica/icons'):
        """Create Emulica application
        
        Arguments:
            ui_path -- the (absolute) path of the directory where the ui 
                       definition file  (emulica.ui) is
            icon_path -- the (absolute) path of the directory where the icons are
        """
        # Default values
        self.filename = None
        self.about = None
        self.adding = None
        self.changed = False
        icon_theme = gtk.icon_theme_get_default()
        icon_theme.prepend_search_path(icon_path)
        
        location = os.path.join(ui_path, 'emulica.ui')
        self.builder = gtk.Builder()
        self.builder.add_from_file(location)
        self.builder.set_translation_domain(application)
        #self.builder = gtk.glade.XML(location, domain=application)
        
        #get some common widgets
        self.window = self.builder.get_object('window')
        #create the statusbar
        self.status = dialogs.EmulicaStatusBar(self)
        # connect signals
        #self.builder.signal_autoconnect(self)
        # setup and initialize our statusbar
        self.status.reset(self.filename)
        self.changed = False
        self.props = dict()
        notebook = self.builder.get_object('main_notebook')
        notebook.connect('switch-page', lambda o, p, p1: self.update_undo_redo_menuitem())
        self.window.set_size_request(800, 600)
        #Create subpart of the application, and connect it to the UI
        self.model = emulation.Model()
        self.emulica_model = modelling.EmulicaModel(self)
        
        self.emulica_control = control.EmulicaControl(self)
        self.preferences = dialogs.EmulicaPreferences(self)
        self.emulica_results = results.EmulicaResults(self)
        # connect signals
        signals_map = list()
        for obj in [self, self.emulica_model, self.emulica_control, self.emulica_results]:
            signals_map += [(f, getattr(obj, f)) for f in dir(obj) if f.startswith('on_')]
        self.builder.connect_signals(dict(signals_map))
        #initialize props and preferences
        self.init_props()
        self.preferences.apply()   
    
    def init_props(self):
        """Initialize the props dictionary with the right values"""        
        clean = False
        if not 'exec' in self.props:
            self.props['exec'] =  dict()
            clean = True
        default = [('limit', 200), 
                   ('real-time', True),
                   ('rt-factor', 2), 
                   ('animate', True)]
        for (prop, val) in default:
            if clean or not prop in self.props['exec']:
                self.props['exec'][prop] = val
            
    def on_window_delete_event(self, widget, event, data = None):
        """When the window is requested to be closed, we need to check if they have 
        unsaved work. We use this callback to prompt the user to save their work 
        before they exit the application. From the 'delete-event' signal, we can 
        choose to effectively cancel the close based on the value we return."""
        if self.check_for_save(): 
            return False # Propagate event
        else:
            return True #block event !
        
    def on_window_destroy(self, widget, data = None):
        gtk.main_quit()
    
    def on_new_activate(self, menuitem, data = None):
        """Callback for the 'New' menuitem. We need to prompt for save if 
        the file has been modified, and then delete the buffer and clear the  
        modified flag.
        """
        if self.check_for_save():        
            self.clear()

    def on_open_activate(self, menuitem, data = None):
        """Callback for the  'Open' menuitem. We need to prompt for save if 
        thefile has been modified, allow the user to choose a file to open, and 
        then call load_file() on that file.
        """    
        if self.check_for_save(): 
            filename = self.get_open_filename()
            if filename: self.load_file(filename)
      
    def on_save_activate(self, menuitem, data = None):
        """Callback for the 'Save' menu item. We need to allow the user to choose 
        a file to save if it's an untitled document, and then call write_file() on that 
        file.
        """    
        if self.filename == None: 
            filename = self.get_save_filename()
            if filename: self.write_file(filename)
        else: self.write_file(self.filename)
        
    def on_saveas_activate(self, menuitem, data = None):
        """Callback for the 'Save As' menu item. We need to allow the user 
        to choose a file to save and then call write_file() on that file.
        """    
        filename = self.get_save_filename()
        if filename: self.write_file(filename)
    
    def on_quit_activate(self, menuitem, data = None):
        """Callback for the 'Quit' menu item. We need to prompt for save if 
        the file has been modified and then break out of the GTK+ main loop          
        """   
        if self.check_for_save(): 
            gtk.main_quit()
    
    def on_undo_activate(self, menuitem, data = None):
        """Callback for the undo menuitem. ATM, only undo in the control code 
        is supported."""
        self.get_context().undo()
        
    def on_redo_activate(self, menuitem, data = None):
        """Callback for the redo menuitem. ATM, only undo in the control code 
        is supported."""
        self.get_context().redo()
        
    def on_cut_activate(self, menuitem, data = None):
        """Callback for the 'Cut' menuitem. Copy selected modules and delete them"""
        self.get_context().cut()
        
    def on_copy_activate(self, menuitem, data = None):
        """Callback for the 'Copy' menuitem. 
        If the modelling panel is displayed, copy the selected model into the paperclip"""
        self.get_context().copy()
        
    def on_paste_activate(self, menuitem, data = None):
        """Callback for the 'Paste' menuitem. 
        If the modelling panel is displayed, paste the content of the paperclip into the model."""
        self.get_context().paste()
       
    def on_delete_activate(self, menuitem, data = None):
        """Called when the user clicks the 'Delete' menu. """ 
        self.get_context().delete()
    
    def on_preferences_menuitem_activate(self, menuitem, data = None):
        """Callback for the 'preference' menuitem. Display the preference dialog."""
        self.preferences.edit()
    
    def on_exec_properties_menuitem_activate(self, menuitem):
        """Callback for the execution settings menuitem. Display a dialog to
        edit execution properties."""
        dialog = dialogs.EmulicaExecSettings(self.window, self.props)
        response = dialog.run()
        if response == gtk.RESPONSE_ACCEPT:
            self.props['exec']['limit'] = dialog.get_limit()
            self.props['exec']['real-time'] = dialog.get_rt()
            self.props['exec']['rt-factor'] = dialog.get_rt_factor()
            self.props['exec']['animate'] = dialog.get_animate()
            self.emulica_model.set_animate(dialog.get_animate())
            self.changed = True
        dialog.destroy()
    
    def on_about_menuitem_activate(self, menuitem, data = None):
        """Called when the user clicks the 'About' menu. We use gtk_show_about_dialog() 
        which is a convenience function to show a GtkAboutDialog. This dialog will
        NOT be modal but will be on top of the main application window.    
        """
        if (not self.about):
            self.about = dialogs.EmulicaAbout(self.window)
        else:
            self.about.present()
        
    def on_start_activate(self, widget, data = None):
        #clean results
        
        #start input redirection
        self.emulica_control.tee_stdout_to_log()
        self.emulica_control.prepare_control()
        #get parameter from preference (self.props dictionary)
        kwargs = {'until': self.props['exec']['limit'],
                  }
        rt = self.props['exec']['real-time']
        kwargs['real_time'] = rt
        if rt: 
            kwargs['rt_factor'] = self.props['exec']['rt-factor']
        else:
            kwargs['step'] = self.props['exec']['animate']
        self.time_controler = controler.TimeControler(self.model, **kwargs)
        self.time_controler.add_callback(self.on_emulation_step, controler.EVENT_TIME)
        self.time_controler.add_callback(self.on_emulation_start, controler.EVENT_START)
        self.time_controler.add_callback(self.on_emulation_finish, controler.EVENT_FINISH)
        self.time_controler.add_callback(self.emulica_results.on_emulation_finish, controler.EVENT_FINISH)
        self.time_controler.add_callback(self.on_emulation_exception, controler.EXCEPTION)
        self.time_controler.start() 
    
    def on_stop_activate(self, widget, data = None):
        self.time_controler.stop()
    
    def on_pause_toggled(self, widget, data = None):
        if widget.get_active():
            #pause simulation
            self.time_controler.pause()
        else:
            #resume simu
            self.time_controler.resume()
            
    def on_emulation_step(self, model):
        """Callback called at regular interval during emulation. Update status 
        bar. use add_idle, because this function is called from another thread."""
        gobject.idle_add(self.status.set_progress, _("running"), model.current_time(), self.props['exec']['limit'])
        
    
    def on_emulation_start(self, model):
        """Callback activated when emulation start. Make pause and stop button 
        sensible. use add_idle, because this function is called from another 
        thread."""
        for button in [self.builder.get_object(name) for name in ['pause', 'stop']]:
            gobject.idle_add(button.set_sensitive, True)
        gobject.idle_add(self.builder.get_object('start').set_sensitive, False)
        gobject.idle_add(self.builder.get_object('reinit').set_sensitive, False)       
        gobject.idle_add(self.status.set_progress, _("starting"))
    
    def on_emulation_finish(self, model):
        """Callback activated when emulation finish. use add_idle, because this 
        function is called from another thread."""
        gobject.idle_add(self.reset_execution)
        gobject.idle_add(self.status.set_progress, _("finished"), model.current_time(), model.current_time())
        gobject.idle_add(self.builder.get_object('reinit').set_sensitive, True)
        #stop input redirection
        gobject.idle_add(self.emulica_control.tee_stdout_to_log, False)
        
    def on_emulation_exception(self, exception, trace):
        """Callback activated when the simulation run encounters an exception.
        Warning!  This is called from an outside thread!!!"""
        #print _("Exception when runing emulation:\n") + str(exception)
        import traceback
        #TODO: format traceback using pango markup
        gobject.idle_add(self.error_message, _("Exception when runing emulation:\n") + str(exception), "".join(traceback.format_list(trace)))
        #self.error_message(_("Exception when runing emulation:\n") + str(exception))
    
    
    def on_reinit_activate(self, widget, data = None):
        """Callback for the clear button (both in menu and tool bar). Initialize
        simulation. Only active when simulation is not running."""
        self.model.clear()
        self.emulica_results.delete_results()
        self.builder.get_object('result_tab_label').set_sensitive(False)
        self.builder.get_object('results_menuitem').set_sensitive(False)
        self.builder.get_object('reinit').set_sensitive(False)
        #we clear also statusbar !
        self.status.set_progress(_("ready"))
        self.builder.get_object('result_tab_label')
    
    def get_context(self):
        """Return emulica_model or emulica_control, according to the visible tab."""
        notebook = self.builder.get_object('main_notebook')
        if (notebook.get_current_page() == 1):
            return self.emulica_control
        else:
            return self.emulica_model
    
    def get_save_filename(self):
        """We call get_save_filename() when we want to get a filename to 
        save from the user. It will present the user with a file chooser 
        dialog and return the filename or None.
        """  
        filename = None
        chooser = gtk.FileChooserDialog(_("Save File..."), self.window,
                                        gtk.FILE_CHOOSER_ACTION_SAVE,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                         gtk.STOCK_SAVE, gtk.RESPONSE_OK))
	chooser.set_do_overwrite_confirmation(True)
        filter_emulica = gtk.FileFilter()
        filter_emulica.set_name("Emulica files")
        filter_emulica.add_pattern("*.emu")
        chooser.add_filter(filter_emulica)
        response = chooser.run()
        if response == gtk.RESPONSE_OK: 
            filename = chooser.get_filename()
        chooser.destroy()
	extension = os.path.splitext(filename)[1]
        if not extension:
	    filename = filename + '.emu'
        return filename
    
    def update_undo_redo_menuitem(self, *args):
        """Callback for context change (emulation/control/result)"""
        redo = self.builder.get_object('redo')
        undo = self.builder.get_object('undo')
        undo.set_sensitive(self.get_context().can_undo())
        redo.set_sensitive(self.get_context().can_redo())
        #TODO: if context is not emulation: inactivate zoom buttons
        
        
    def error_message(self, message, details = None):
        """We call error_message() any time we want to display an error message to 
        the user. It will both show an error dialog and log the error to the 
        terminal window.
        
        Arguments:
            message -- the main message to display
            details -- error details (such as traceback information)
        """
        # create an error message dialog and display modally to the user
        dialog = gtk.MessageDialog(self.window,
                                   gtk.DIALOG_DESTROY_WITH_PARENT,
                                   gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, message)
        if details:
            dialog.format_secondary_text(details)
        logger.warning(message)
        logger.info(details)
        #we don't spawn a new event loop, because it causes freeze when called from idle_add
        dialog.connect('response', lambda d, r: d.destroy())
        dialog.show()
        return False
        
    
        
    def check_for_save (self):
        """This function will check to see if the model has been
        modified and prompt the user to save if it has been modified.
        It return true if the action can continue, false otherwise"""
        if self.changed:
            if self.filename:
                docname = os.path.basename(self.filename)
            else:
                docname = _("untitled")
            dialog = gtk.MessageDialog(self.window, 
                                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                                gtk.MESSAGE_WARNING,
                                gtk.BUTTONS_NONE,
                                _("Do you want to save modifications in document {0} before closing?".format(docname)))
            dialog.add_buttons(_("Close without saving"), gtk.RESPONSE_REJECT,
                                 gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                 gtk.STOCK_SAVE, gtk.RESPONSE_ACCEPT)
            dialog.format_secondary_text(_("If you don't save all modifications will be lost."))
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_ACCEPT:
                self.on_save_menuitem_activate(None, None)
                return True
            elif response == gtk.RESPONSE_CANCEL:
                return False
            elif response == gtk.RESPONSE_REJECT:
                return True
        else:
            return True 
    
    
            
    def get_open_filename(self):
        """We call get_open_filename() when we want to get a filename to open 
        from the user. It will present the user with a file chooser dialog
        and return the filename or None.
        """
        filename = None
        chooser = gtk.FileChooserDialog(_("Open File..."), self.window,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                         gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        filter_emulica = gtk.FileFilter()
        filter_emulica.set_name("Emulica files")
        filter_emulica.add_pattern("*.emu")
        filter_all = gtk.FileFilter()
        filter_all.set_name("All files")
        chooser.add_filter(filter_emulica)
        chooser.add_filter(filter_all)
        response = chooser.run()
        if response == gtk.RESPONSE_OK: 
            filename = chooser.get_filename()
        chooser.destroy()
        
        return filename
    
    
        
    def clear(self):
        """Reset the model, control and properties attributes of the 
        application."""
        while gtk.events_pending(): gtk.main_iteration()
        self.model = emulation.Model()
        self.props = dict()
        self.filename = None
        self.emulica_model.reset(self.model)
        self.emulica_control.reset(self.model)
        self.builder.get_object('result_tab_label').set_sensitive(False)
        self.builder.get_object('results_menuitem').set_sensitive(False)
        self.builder.get_object('main_notebook').set_current_page(0)
    
    def load_file(self, filename):
        """We call load_file() when we have a filename and want to load a model
        from that file. The previous contents are overwritten.    
        """
        # add Loading message to status bar and ensure GUI is current
        self.status.set_text(_("Loading {0}").format(filename))
        while gtk.events_pending(): 
            gtk.main_iteration()
        #open filename, verify archive integrity
        d = os.path.dirname(filename)
        if d != '':
            os.chdir(d)
        filename = os.path.basename(filename)
        gsfile = emuML.EmuFile(filename, 'r')
        #TODO: verify if submodels are readable, and propose to relocate them if nessecary
        try:
            (self.model, control) = gsfile.read()
            self.filename = filename
            properties = gsfile.get_properties()
            #filter layout properties: if the  module is not in the model drop the position
            top_layout = properties['main']['layout']
            for name in top_layout.keys():
                if not name in self.model.modules.keys():
                    del top_layout[name]
                    logger.warning(_("module {name} present in layout was not found. removing from layout.").format(name = name))
            #for each property, get the layout, and replace modules names by modules instances
            self.props = properties.pop('main')
            self.init_props()
            self.reset_execution()
            #introduce a function that convert module names in module instance...
            def convert_to_layout(model, d):
                r = dict()
                mod_list = [module.name for module in model.module_list()]
                for (name, position) in d.items():
                    if name in mod_list:
                        r[model.get_module(name)] = position
                return r
            if 'layout' in self.props:#some model might not have the layout property
                main_layout = convert_to_layout(self.model, self.props['layout'])
            else:
                logger.warning(_("model did not have any layout."))
                main_layout = {}
            sub_layout = dict()
            #get layouts from files
            for (name, prop) in properties.items():
                submodel = self.model.get_module(name)
                layout = convert_to_layout(submodel, prop['layout'])
                sub_layout[submodel] = layout
            #first create the widgets
            self.emulica_model.reset(self.model, main_layout, sub_layout)
            #init control buffer
            self.emulica_control.reset(self.model, control)
            
        except emuML.EmuMLError, warning:
            # error loading file, show message to user
            self.error_message (_("Could not open file: {filename}s\n {warning}").format(filename = filename, warning = warning))
        finally:
            gsfile.close()
        # clear loading status and restore default
        self.changed = False
        self.status.reset(self.filename)

    def write_file(self, filename):
        """Write model, properties and control buffer to a file."""
        
        # add Saving message to status bar and ensure GUI is current
        if filename: 
            self.status.set_text(_("Saving {0}").format(filename))
        else:
            self.status.set_text(_("Saving {0}").format(self.filename))
        while gtk.events_pending(): 
            gtk.main_iteration()
            
        self.props['layout'] = self.emulica_model.get_layout()  
        gsfile = emuML.EmuFile(filename, 'w')
        try:
            gsfile.write(self.model, self.emulica_control.get_text(), self.props)
        except Exception, msg:
            print msg
            self.error_message(_("Could not save file: {0}").format(filename))
        finally:
            gsfile.close()
        # clear saving status and restore default     
        self.changed = False
        self.status.reset(filename)
        self.filename = filename
    
    def reset_execution(self):
        """Reset the execution state"""
        for button in [self.builder.get_object(name) for name in ['pause', 'stop']]:
            button.set_sensitive(False)
        self.builder.get_object('start').set_sensitive(True)
        img = self.builder.get_object('syntax_check_image')
        img.set_from_stock(gtk.STOCK_DIALOG_QUESTION, gtk.ICON_SIZE_BUTTON)
        
    def main(self, source_file = None):
        """Launch the main gtk event loop"""
        gtk.gdk.threads_enter()
        self.window.show()
        if source_file:
            self.load_file(source_file)
        gtk.main()
        gtk.gdk.threads_leave()
        


