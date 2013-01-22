#!/usr/bin/env python
# *-* coding: iso-8859-15 *-*

# emulicapp/modelling.py
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
emulica is a graphical application to the emulica framework, build using GTK. This (sub) module 
contains functions that pertainng to modelling.
"""

import sys, os, logging
from emulica import canvas, emuML, emulation
from emulica.properties import PropertiesDialog
import dialogs
import gtk, gobject
logger = logging.getLogger('emulica.emulicapp.modelling')

class EmulicaModel:
    """Graphical application for emulica: Modelling part.
    
    Attributes:
        main -- the Emulica main application
        builder -- the GtkBuilder object
        cmd_manager -- undo/redo manager
        canvas -- the model canvas  (EmulicaCanvas)
        clipboard -- the module clipboard
    """

    def __init__(self, main_app):
        """Create the modeling widget, connect signal, and add an empty model"""
        self.main = main_app
        self.builder = main_app.builder
        self.model = main_app.model
        self.cmd_manager = CommandManager()
        self.cmd_manager.handler = self.main.update_undo_redo_menuitem
        self.canvas = canvas.EmulicaCanvas(self.model, self.cmd_manager)
        self.canvas.connect('selection-changed', self.on_emulation_selection_changed)
        self.canvas.connect('add-done', self.on_emulation_add_done)
        self.clipboard = gtk.Clipboard(selection = '_SEME_MODULE_CLIPBOARD')
        gobject.timeout_add(1500, self.check_clipboard)
        model_view = self.builder.get_object('model_view')
        #TODO: connect signal changed
        self.canvas.contextmenu = self.builder.get_object('emulation_contextmenu')
        model_view.add(self.canvas)
        self.canvas.show()
        
    def reset(self, model, main_layout = None, sub_layout = None):
        """Reset the model"""
        self.model = model
        self.canvas.setup_model(self.model)
        #then apply the layouts
        if (main_layout != None):
            self.canvas.apply_layout(main_layout)
        if (sub_layout != None):    
            for (submodel, layout) in sub_layout.items():
                self.canvas.apply_layout(layout, submodel = submodel)   
        #TODO: clear the command stack
    
    def get_layout(self):
        """Wrapper around the canvas get_layout function"""
        return self.canvas.get_layout()
       
    def set_animate(self, option):
        """Set wether the simulation should be animated or not"""
        self.canvas.animate = option
       
    def check_clipboard(self):
        """This method repetitively check for text in the special 
        _SEME_MODULE_CLIPBOARD clipboard, and set paste button accordingly
        """
        widget = self.builder.get_object('paste')
        def callback(clipboard, text, data):
            if text == None or text == '':
                widget.set_sensitive(False)
            else:
                widget.set_sensitive(True)
        self.clipboard.request_text(callback)
        return True
    
    def on_import_emulation_menuitem_activate(self, menuitem, data = None):
        """Callback for the imports emulation model menuitem."""
        chooser = gtk.FileChooserDialog(_("Import emulation model..."), self.main.window,
                                        gtk.FILE_CHOOSER_ACTION_OPEN,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                         gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            #change dir to the dir of the imported model
            filename = chooser.get_filename()
            os.chdir(os.path.dirname(filename))
            self.model = emuML.load(filename)
            self.canvas.setup_model(self.model)
        chooser.destroy()
        
    def on_export_emulation_menuitem_activate(self, menuitem, data = None):
        """Callback for the export emulation menuitem."""
        chooser = gtk.FileChooserDialog(_("Export emulation model..."), self.main.window,
                                        gtk.FILE_CHOOSER_ACTION_SAVE,
                                        (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
                                         gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        if self.main.filename:
            chooser.set_filename(os.path.splitext(self.main.filename)[0]+'.xml')
        response = chooser.run()
        if response == gtk.RESPONSE_OK: 
            emuML.save(self.model, chooser.get_filename())
        chooser.destroy()

    def undo(self):
        """Undo"""
        self.cmd_manager.undo()
        
    def redo(self):
        """Redo"""
        self.cmd_manager.redo()
        
    def can_undo(self):
        """Return True if there are undoable actions."""
        return self.cmd_manager.can_undo()
        
    def can_redo(self):
        """Return True if there are rendoable actions."""
        return self.cmd_manager.can_redo()
        
    def cut(self):
        """Cut"""
        self.canvas.cut_clipboard(self.clipboard)
        
    def copy(self):
        """Copy"""
        self.canvas.copy_clipboard(self.clipboard)

    def paste(self):
        """Paste"""
        self.canvas.paste_clipboard(self.clipboard)
        
    def delete(self):
        """Delete""" 
        self.canvas.delete_selection()

    def on_zoom_in_activate(self, menuitem):
        """Callback for the zoom in menuitem. increment scale."""
        scale = self.canvas.get_scale() * 1.25
        self.canvas.set_scale(scale)
        self.adjust_canvas_size()
        
    def on_zoom_out_activate(self, menuitem):
        """Callback for the zoom in menuitem. increment scale."""
        scale = self.canvas.get_scale() / 1.25
        self.canvas.set_scale(scale)
        self.adjust_canvas_size()
    
    def on_zoom_100_activate(self, menuitem):
        """Callback for the zoom in menuitem. increment scale."""
        self.canvas.set_scale(1)
        self.adjust_canvas_size()
    
    def on_zoom_fit_activate(self, menuitem):
        """Callback for the zoom fit menuitem. Set scale and scrolled window
        adjustment to fit the model canvas."""
        (x1, y1, x2, y2) = self.canvas.fit_size() 
        vp = self.builder.get_object('model_view')
        vadj = vp.get_vadjustment()
        hadj = vp.get_hadjustment()
        hscale = hadj.page_size / float(x2 - x1) 
        vscale = vadj.page_size / float(y2 - y1) 
        self.canvas.set_scale(min(hscale, vscale))
        self.adjust_canvas_size()
        s = self.canvas.get_scale()
        hadj.value = x1 * s
        vadj.value = y1 * s
    
    def adjust_canvas_size(self): 
        scale = self.canvas.get_scale()
        (x1, y1, x2, y2) = self.canvas.get_bounds()
        self.canvas.set_size_request(int((x2 - x1) * scale), int((y2 - y1) * scale))
        
    def on_button_actuator_activate(self, widget, data = None):
        """Change arrow orientation and change visibility of table"""
        palette_actuator_table = self.builder.get_object('table_actuator')
        palette_actuator_arrow = self.builder.get_object('arrow_actuator')
        if palette_actuator_table.props.visible:
            palette_actuator_table.hide()
            palette_actuator_arrow.set(gtk.ARROW_RIGHT, gtk.SHADOW_OUT)
        else:
            palette_actuator_table.show()
            palette_actuator_arrow.set(gtk.ARROW_DOWN, gtk.SHADOW_OUT)
    
    def on_button_holder_activate(self, widget, data = None):
        """Change arrow orientation and change visibility of table"""
        palette_holder_arrow = self.builder.get_object('arrow_holder')
        palette_holder_table = self.builder.get_object('table_holder')
        
        if palette_holder_table.props.visible:
            palette_holder_table.hide()
            palette_holder_arrow.set(gtk.ARROW_RIGHT, gtk.SHADOW_OUT)
        else:
            palette_holder_table.show()
            palette_holder_arrow.set(gtk.ARROW_DOWN, gtk.SHADOW_OUT)
    
    def on_button_observer_activate(self, widget, data = None):
        """Change arrow orientation and change visibility of table"""
        palette_observer_arrow = self.builder.get_object('arrow_observer')
        palette_observer_table = self.builder.get_object('table_observer')
        if palette_observer_table.props.visible:
            palette_observer_table.hide()
            palette_observer_arrow.set(gtk.ARROW_RIGHT, gtk.SHADOW_OUT)
        else:
            palette_observer_table.show()
            palette_observer_arrow.set(gtk.ARROW_DOWN, gtk.SHADOW_OUT)
    
    def on_add_submodel_activate(self, button):
        """Callback for the 'add submodel' button"""
        #display file chooser, and parse file
        sub_file = self.main.get_open_filename()
        #make subfile a relative path
        name = "Submodel"+str(len(self.model.modules))
        gsf = emuML.EmuFile(sub_file, 'r', parent_model = self.model, name = name)
        (submodel, subcontrol) = gsf.read()   
        for (name, prop) in gsf.get_properties().items():
            submodel = self.model.get_module(name)
            layout = dict()
            for (mod_name, position) in prop['layout'].items():
                if submodel.has_module(mod_name):
                    module = submodel.get_module(mod_name)
                    layout[module] = position
            #then apply the layouts
            self.canvas.apply_layout(layout, submodel = submodel)
        emuML.compile_control(submodel, subcontrol)
        
    def on_add_create_toggled(self, widget, data = None):
        self.add_module(widget, 'create_tb', emulation.CreateAct)
    
    def on_add_dispose_toggled(self, widget, data = None):
        self.add_module(widget, 'dispose_tb', emulation.DisposeAct)
    
    def on_add_shape_toggled(self, widget, data = None):
        self.add_module(widget, 'shape_tb', emulation.ShapeAct)
            
    def on_add_space_toggled(self, widget, data = None):
        self.add_module(widget, 'space_tb', emulation.SpaceAct)
            
    def on_add_assy_toggled(self, widget, data = None):
        self.add_module(widget, 'assemble_tb', emulation.AssembleAct)
    
    def on_add_unassy_toggled(self, widget, data = None):
        self.add_module(widget, 'unassy_tb', emulation.DisassembleAct)
                
    def on_add_holder_toggled(self, widget, data = None):
        self.add_module(widget, 'fifo_tb', emulation.Holder)
    
    def on_add_failure_toggled(self, widget, data = None):
        self.add_module(widget, 'failure_tb', emulation.Failure)
    
    def on_add_pushobs_toggled(self, widget, data = None):
        self.add_module(widget, 'pushobs_tb', emulation.PushObserver)
    
    def on_add_pullobs_toggled(self, widget, data = None):
        self.add_module(widget, 'pullobs_tb', emulation.PullObserver)
    
    def add_module(self, widget, my_tb, mod_type):
        """Set the canvas in 'adding mode'."""
        tb_list = ['create_tb', 'dispose_tb', 'shape_tb', 'space_tb', 'assemble_tb', 'unassy_tb', 'fifo_tb', 'failure_tb', 'pushobs_tb', 'pullobs_tb']
        tb_list.remove(my_tb)
        if widget.get_active():
            for tb_name in tb_list:
                tb = self.builder.get_object(tb_name)
                tb.set_active(False)
                self.canvas.set_adding(True, mod_type)
        else:
            self.canvas.set_adding(False)
            
    def on_properties_activate(self, menuitem, data = None):
        """Properties button or menuitem is activated (or clicked)"""
        #get module from selection
        for module in self.canvas.selection:
            prop_win = PropertiesDialog(self.main.window, module, self.model, self.cmd_manager)
            prop_win.show()
            self.changed = True
            
    def on_model_properties_activate(self, menuitem, data = None):
        """Properties of a model"""
        dialogs.ModelPropertiesDialog(self.main.window, self.model, self.cmd_manager)
        self.changed = True
            
    def on_emulation_selection_changed(self, selection):
        """Callback for change in the selection of modules.
        Change sensitivity of some buttons
        """
        value = not len(selection) == 0
        widgets_names = ['properties', 
                         'cut', 
                         'copy',
                         'delete']
        for name in widgets_names:
            widget = self.builder.get_object(name)
            widget.set_sensitive(value)
    
    def on_emulation_add_done(self):
        """Callback connect to the add-done signal of the model canvas."""
        tb_list = ['create_tb', 'dispose_tb', 'shape_tb', 'space_tb', 'assemble_tb', 'unassy_tb', 'fifo_tb', 'pushobs_tb', 'pullobs_tb']
        for tb_name in tb_list:
            tb = self.builder.get_object(tb_name)
            tb.set_active(False)
    
    
class CommandManager:
    """This class implements the pattern Command to access to create destroy and
    modify the emulation model and canvas.
    
    The command interface :
        __init__() -- create the Command object and execute the command
        undo() -- undo the command
        redo() -- redo the command
    
    Attributes:
        undo_stack -- a stack of undoable actions
        redo_stack -- a stack of redoable actions
        
    """
    def __init__(self):
        """Create a new instance of the Emulation command manager"""
        self.undo_stack = []
        self.redo_stack = []
        def fake_handler():
            pass
        self.handler = fake_handler
        
    def undo(self):
        """Undo last command."""
        cmd = self.undo_stack.pop()
        cmd.undo()
        self.redo_stack.append(cmd)
        self.handler()
        
    def redo(self):
        """Redo last redone command."""
        cmd = self.redo_stack.pop()
        cmd.redo()
        self.undo_stack.append(cmd)
        self.handler()
    
    def add_cmd(self, cmd):
        self.undo_stack.append(cmd)
        del self.redo_stack[0:len(self.redo_stack)]
        self.handler()
    
    def can_undo(self):
        return len(self.undo_stack) > 0
        
    def can_redo(self):
        return len(self.redo_stack) > 0
    
    def create_module(self, name, moduletype, model):
        """Create a new module and add it to the canvas."""
        #init : create module (it is automatically added to the model)...
        #undo : remove module from  model
        #redo : put module back in model
        
        class CreateCmd:
            def __init__(self, name, moduletype, model):
                self.module = moduletype(model, name)
                self.model = model
                
            def undo(self):
                self.model.unregister_emulation_module(self.module.fullname())
                
            def redo(self):
                model.register_emulation_module(self.module)
        
        cmd = CreateCmd(name, moduletype, model)
        self.add_cmd(cmd)
        
        
    def delete_module(self, module, model):
        """Delete a module from the model and canvas"""
        #init : remove module from canvas and model
        #undo : put module back in model and canvas
        #redo : same as do
        class DeleteCmd:
            def __init__(self, module, model):
                self.module = module
                self.model = model
                self.model.unregister_emulation_module(self.module.fullname())
                
            def undo(self):
                self.model.register_emulation_module(self.module)
                
            def redo(self):
                self.model.unregister_emulation_module(self.module.fullname())
            
        cmd = DeleteCmd(module, model)
        self.add_cmd(cmd)
        
    def rename_module(self, module, new_name):
        """Change module name"""
        class RenameCmd:
            def __init__(self, module, new_name):
                self.module = module
                self.old_name = module.name
                self.name = new_name
                self.module.rename(new_name)
            
            def undo(self):
                self.module.rename(self.old_name)
                
            def redo(self):
                self.module.rename(self.name)
        
        cmd = RenameCmd(module, new_name)
        self.add_cmd(cmd)
        
    def change_prop(self, registry, prop_name, prop_value):
        """Modify a module property"""
        #do : get property old_value (if it exists !), set new value
        #undo : set prop to old_value
        #redo : set prop to new_value
        #clear : forget old_value
        class ChangePropCmd:
            def __init__(self, registry, prop_name, value):
                self.registry = registry
                self.name = prop_name
                if self.name in registry.keys():
                    self.old_value = registry[self.name]
                else:
                    self.old_value = None
                self.value = value
                self.registry[self.name] = self.value
            
            def undo(self):
                self.registry[self.name] = self.old_value
                
            def redo(self):
                self.registry[self.name] = self.value
        
        cmd = ChangePropCmd(registry, prop_name, prop_value)
        self.add_cmd(cmd)
    
    def change_prop_name(self, registry, old_name, new_name):
        """Modify a module property"""
        #do : delete old prop, add new
        #undo : delete new add old
        #redo : same as do
        class ChangePropNameCmd:
            def __init__(self, registry, old_name, new_name):
                self.registry = registry
                self.old_name = old_name
                self.new_name = new_name
                value = self.registry[self.old_name]
                del self.registry[self.old_name]
                self.registry[self.new_name] = value
            
            def undo(self):
                value = self.registry[self.new_name]
                del self.registry[self.new_name]
                self.registry[self.old_name] = value
               
            def redo(self):
                value = self.registry[self.old_name]
                del self.registry[self.old_name]
                self.registry[self.new_name] = value
        
        cmd = ChangePropNameCmd(registry, old_name, new_name)
        self.add_cmd(cmd)
    
    
    def del_prop(self, registry, prop_name):
        """Delete a property from a Registry"""
        #do : get property old_value, delete
        #undo : add prop with old_value
        #redo : delete
        class DelPropCmd:
            def __init__(self, registry, prop_name):
                self.registry = registry
                self.name = prop_name
                self.old_value = registry[self.name]
                del self.registry[self.name]
            
            def undo(self):
                self.registry[self.name] = self.old_value
                
            def redo(self):
                del self.registry[self.name]
        
        cmd = DelPropCmd(registry, prop_name)
        self.add_cmd(cmd)
        
    def add_prop(self, registry, prop_name, prop_value):
        """Modify a module property"""
        #do : add
        #undo : delete
        #redo : add
        class AddPropCmd:
            def __init__(self, registry, prop_name, value):
                self.registry = registry
                self.name = prop_name
                self.value = value
                self.registry[self.name] = self.value
            
            def undo(self):
                del self.registry[self.name]
                
            def redo(self):
                self.registry[self.name] = self.value
        
        cmd = AddPropCmd(registry, prop_name, prop_value)
        self.add_cmd(cmd)
    
    def add_prog(self, p_table, name, delay, transform = None):
        """Add a new program in p_table"""
        #do : add prog in prog_table
        #undo : del prog from p_tbale
        #redo : add prog in p_table
        class AddProgCmd:
            def __init__(self, p_table, name, delay, transform):
                self.p_table = p_table
                self.name = name
                self.p_table.add_program(self.name, delay, transform)
                if name in self.p_table:
                    self.prog = self.p_table[name]
                else:
                    self.prog = None
            
            def undo(self):
                del self.p_table[self.name]
                
            def redo(self):
                if self.prog is None:
                    del self.p_table[self.name]
                else:
                    self.p_table[self.name] = self.prog
        
        cmd = AddProgCmd(p_table, name, delay, transform)
        self.add_cmd(cmd)
    
    def del_prog(self, p_table, name):
        """Remove program from p_table"""
        #do : del prog in prog_table, remember value
        #undo : add prog from p_tbale
        #redo : del prog in p_table
        class DelProgCmd:
            def __init__(self, p_table, name):
                self.p_table = p_table
                self.name = name
                self.prog = self.p_table[self.name]
                del self.p_table[self.name]
            
            def undo(self):
                self.p_table[self.name] = self.prog
                
            def redo(self):
                del self.p_table[self.name]
        
        cmd = DelProgCmd(p_table, name)
        self.add_cmd(cmd)
        
    def change_prog_time(self, prog, time):
        """Change the time law of the prog"""
        #do : change time, remember old val
        #undo : set old val
        #redo : set val
        class ChangeProgTimeCmd:
            def __init__(self, prog, time):
                self.prog = prog
                self.time = time
                self.old_time = prog.time_law
                self.prog.time_law = self.time
            
            def undo(self):
                self.prog.time_law = self.old_time
                
            def redo(self):
                self.prog.time_law = self.time
        
        cmd = ChangeProgTimeCmd(prog, time)
        self.add_cmd(cmd)
    
    def change_prog_name(self, t_prog, old_name, new_name):
        """Change the name of a program"""
        #do : del old_name, add new_name
        #undo : del new_name, add old_name
        #redo : same as do
        class ChangeProgNameCmd:
            def __init__(self, t_prog, old_name, new_name):
                self.t_prog = t_prog
                self.old_name = old_name
                self.new_name = new_name
                prog = t_prog[old_name]
                del t_prog[old_name]
                t_prog[new_name] = prog
            
            def undo(self):
                prog = t_prog[new_name]
                del t_prog[new_name]
                t_prog[old_name] = prog
                
            def redo(self):
                prog = t_prog[old_name]
                del t_prog[old_name]
                t_prog[new_name] = prog
        
        cmd = ChangeProgNameCmd(t_prog, old_name, new_name)
        self.add_cmd(cmd)
    
    
    def add_setup(self, t_setup, initial, final, time):
        """Add the (initial, final, time) setup in t_setup"""
        #do : add
        #undo : delete
        #redo : same as do
        class AddSetupCmd:
            def __init__(self, t_setup, initial, final, time):
                self.t_setup = t_setup
                self.setup = (initial, final, time)
                self.t_setup.add(*(self.setup))
                
            def undo(self):
                self.t_setup.remove(self.setup[0], self.setup[1])
                
            def redo(self):
                self.t_setup.add(*(self.setup))
        
        cmd = AddSetupCmd(t_setup, initial, final, time)
        self.add_cmd(cmd)
        
    def del_setup(self, t_setup, initial, final):
        """Add the (initial, final, time) setup in t_setup"""
        #do : add
        #undo : delete
        #redo : same as do
        class DelSetupCmd:
            def __init__(self, t_setup, initial, final):
                self.t_setup = t_setup
                time = self.t_setup.get(initial, final)
                self.setup = (initial, final, time)
                self.t_setup.remove(self.setup[0], self.setup[1])
                
            def undo(self):
                self.t_setup.add(*(self.setup))
                
            def redo(self):
                self.t_setup.remove(self.setup[0], self.setup[1])
        
        cmd = DelSetupCmd(t_setup, initial, final)
        self.add_cmd(cmd)
        
    def change_setup(self, t_setup, initial, final, new_initial = None, new_final = None, new_time = None):
        """Change setup"""
        #do : call change with new values
        #undo : call change with old values
        #redo : same as do
        class ChangeSetupCmd:
            def __init__(self, t_setup, initial, final, new_initial = None, new_final = None, new_time = None):
                self.t_setup = t_setup
                time = self.t_setup.get(initial, final)
                self.old = [initial, final, time]
                self.new = [new_initial or initial, new_final or final, new_time or time]
                self.t_setup.modify(*(self.__create_args(self.old, self.new)))
                
            def undo(self):
                self.t_setup.modify(*(self.__create_args(self.new, self.old)))
                
            def redo(self):
                self.t_setup.modify(*(self.__create_args(self.old, self.new))) 
        
            def __create_args(self, old, new):
                return old[0:2]+new
                
        cmd = ChangeSetupCmd(t_setup, initial, final, new_initial, new_final, new_time)
        self.add_cmd(cmd)
    
        
    def modify_canvas_layout(self, layout, canvas):
        """Modify module position"""
        pass
    
