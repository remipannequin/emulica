#!/usr/bin/env python
# *-* coding: iso-8859-15 *-*

# properties.py
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
This module contain classes related to the creation, management and displaying of
properties in emulica.
"""

import random, logging, locale, re, gettext
import gtk
import emulation
gettext.install('emulica')
logger = logging.getLogger('emulica.properties')

class Registry(dict):
    """
    Properties can be attached to every products and module (including models).
    They basically consist in a (name, value) pair. Moreover, a PropertyDisplay 
    can also be used. If so the property is said to be "displayable";
    such properties can be presented in the user interface, and modified. 
    Properties that don't have any PropertyDisplay object associated are not 
    displayed by the PropertyWindow UI.
     
    Properties can be a direct value (a str, bool, int or float) a module (ie a
    pointer to a module), a string that can be evaluated (in a pythonic syntax),
    or complex object that contain other (sub)properties (setup or program 
    tables).  
    
    A property can be accessed from its owner using square braquets [], using 
    its name.
    For example, create['destination'] returns the value of the 'destination'
    property of module 'create'. Shape1['program_table']['program1'] is the 
    property 'program1' of the program_table object (which is in turn the 
    property 'program_table' of module 'Shape1')... Properties can be get/set
    using the square braquet syntax, in the same way a python dictionary can be
    used.
    
    module['prop'] return the non evaluated value of the property. To evaluate
    the property string, the evaluate_property function must be used, or 
    alternativelly, the property must be called. Therefore if module['prop'] is
    "product['mass'] + 5", module['prop'](context) is 12, in context wherethe 
    current product has a property that evaluates to 7.
    
    Classes:
        Registry -- a dict of properties, with dsiplay information
        SetupMatrix -- Models setup (transtion between programs), and associated time 
        Program -- Models actions done by actuators
        Display -- display information for properties
    
    """
    
    def __init__(self, owner, rng):
        """Create a new Registry, where properties can be stored.
        
        Arguments:
            owner -- the module that own this property registry
            parent -- the parent registry (used to get evaluation context and to
            notify owner of property modification)
            
            
        """
        dict.__init__(self)
        assert(owner != None)
        self.owner = owner
        self.rng = rng
        self.displays = dict()
        self.__ordered_display = list()
        self.auto_eval = set()
    
    
    def __getitem__(self, name):
        """Return the property (unevaluated), or the aveluated value if the property has been marqued."""
        if name in self.auto_eval:
            return self.evaluate(name)
        else:
            return dict.__getitem__(self, name)
    
    def __setitem__(self, name, value):
        """call the method of the underling dict, and trigger the modules
        property changed signal."""
        dict.__setitem__(self, name, value)
        self.notify_owner(name)
        
    def notify_owner(self, prop_name):
        """Notify owner or parent of property change"""
        if 'emit' in dir(self.owner):
            self.owner.emit(emulation.Module.PROPERTIES_CHANGE_SIGNAL, prop_name, self.owner)
    
    def set_auto_eval(self, name, auto_eval = True):
        """Mark the property 'name' to be automatically evaluated"""
        if auto_eval:
            self.auto_eval.add(name)
        else:
            self.auto_eval.remove(name)
    
    def add_with_display(self, name, display_type, value = None, display_name = None):
        """Add a new property and set its display. If value is not specified or None,
        it is instancied from the default_value dict in class Display. If display_name
        is not specified or None, it take avlue name.
        
        Arguments:
            name -- the property name
            display_type -- the display type (int, see properties.Display)
            
        Keyword arguments:
            value -- the property's value
            display_name -- the name to use in dialogs
        
        """
        if value is None:
            if 'program_keyword' in dir(self.owner):
                schema = self.owner.program_keyword
            else:
                 schema = list()       
            value = Display.default_value[display_type](self.owner.properties, name, schema)
        display_name = display_name or name
        self[name] = value
        display = Display(display_type, display_name)
        self.__ordered_display.append(name)
        self.displays[name] = display 
    
    def set_display(self, name, display):
        """Set the display of the property designed by 'name'.
        
        Arguments:
            name -- the name of the property
            display -- the properties.Display to set
        """
        self.displays[name] = display
        if not display in self.__ordered_display:
            self.__ordered_display.append(name)
    
    def get_display(self, name):
        """Get the display of the property designed by name.
        
        Arguments:
            name -- the name of the property
            
        Returns:
            the associated Display object, or None if the property is not 
            displayable
        """
        return self.displays[name]
    
    def displayables(self):
        """return a list of (name, value, display) tuple of all the properties
        that have a display set."""
        result = list()
        for name in self.__ordered_display:
            result.append((name, self[name], self.displays[name]))
        return result
    
    def get(self, name):
        """Return the value of the prop without evaluation"""
        return dict.__getitem__(self, name)
    
    def evaluate(self, name, product = None):
        """Resolve reference to other properties, and return the value.
        """
        return self.eval_expression(self.get(name), product)
    
    def eval_and_set(self, name, value, product = None):
        """Evaluate value in the context of product, and set the result as prop 
        name.
        
        Exemple product.properties.eval_and_set('mass', 'self['mass'] / 2')
        """
        self[name] = self.eval_expression(value, product)
    
    def eval_expression(self, expr, product = None):
        """Evaluate expression expr"""
        if type(expr) == str:
            context = dict()
            context['rng'] = self.rng
            if self.owner and 'model' in dir(self.owner):
                context['model'] = self.owner.model
            for (name, value) in self.items():
                context[name] = value
            if not product == None:
                context['product'] = product
            result = eval(expr, globals(), context)
        else:
            result = expr
        return result       
        
    
class SetupMatrix():
    """A Setup Matrix record setup times between programs. 
    When a transition is not found, a default time is used instead
    
    Attributes:
        default_time -- default setup time when no setup data have been found
    
    """
    def __init__(self, prop_registry, default_time = 0, parent_prop_name = 'setup'):
        """Create a new instance of SetupMatrix
        
        Arguments:
            default_time -- default setup time (default = 0)
        
        """
        self.registry = prop_registry
        assert(type(parent_prop_name) == str)
        assert('notify_owner' in dir(self.registry))
        self.parent_prop_name = parent_prop_name
        self.default_time = default_time
        self.__source_prog = dict()
  
    def add(self, initial_prog, final_prog, setup_time):
        """Add a new element in the matrix.
        
        Arguments:
            initial_prog -- the program at the beginig of the setup
            final_prog -- the program at the end of the setup
            setup_time -- the setup delay
        
        """
        if not self.__source_prog.has_key(initial_prog):
            self.__source_prog[initial_prog] = dict()
        self.__source_prog[initial_prog][final_prog] = setup_time
        self.registry.notify_owner(self.parent_prop_name)
    
    def remove(self, initial_prog, final_prog):
        """Remove an element in the setup matrix
        
        Attributes:
            initial_prog -- the program at the beginig of the setup
            final_prog -- the program at the end of the setup
        
        """
        del self.__source_prog[initial_prog][final_prog]
        if len(self.__source_prog[initial_prog]) == 0:
            del self.__source_prog[initial_prog]
        self.registry.notify_owner(self.parent_prop_name)
    
    def modify(self, initial_prog, final_prog, new_initial=None, new_final=None, new_time=None):
        """Change an entry in the setup matrix. If the change create a conflict..."""
        #TODO: check for duplicate keys
        
        time = self.__source_prog[initial_prog][final_prog]
        if (new_initial and (not new_initial == initial_prog)) or (new_final and (not new_final == final_prog)):
            initial = new_initial or initial_prog
            final = new_final or final_prog
            logger.debug(_("changing setup: ({initial}, {final}) -> ({new_init}, {new_final})").format(initial = initial_prog, 
                                                                                                       final = final_prog,
                                                                                                       new_init = initial,
                                                                                                       new_final = final))
            self.remove(initial_prog, final_prog)
            self.add(initial, final, time)
        if new_time:
            logger.debug(_("changing setup time: {0:f}) -> {1:f}").format(time, new_time))
            self.__source_prog[initial_prog][final_prog] = new_time
        self.registry.notify_owner(self.parent_prop_name)
    
    def get(self, initial_prog, final_prog):
        """Get setup time. if initial or final element desn't exist in 
        the matrix, the default value is returned.
        
        Arguments:
            initial_prog -- the program at the beginig of the setup
            final_prog -- the program at the end of the setup
            
        Returns:
            the setup delay
            
        """
        if initial_prog == final_prog:
            return 0
        if self.__source_prog.has_key(initial_prog):
            if self.__source_prog[initial_prog].has_key(final_prog):
                expr = self.__source_prog[initial_prog][final_prog]
            else:
                expr = self.default_time
        else:
            expr = self.default_time
        return self.registry.eval_expression(expr)

    def items(self):
        """Return a list of tuple of the form (initial, final, delay)
        """
        for (initial, d) in self.__source_prog.items():
            for (final, delay) in d.items():
                yield (initial, final, delay)    
    
    def __len__(self):
        """Return the number of elements in the matrix (ie the number of setups)"""
        result = 0
        for d in self.__source_prog.values():
            result += len(d)
        return result
    
    
class XTable(dict):
    """A dictionary of Physical Changes, where the name is the attribute to 
    change and value is the new attribute value. This class is the base for 
    ProgramTable and ChangeTable"""
    
    def __init__(self, prop_registry, parent_prop_name):
        """Create a new Xtable.
        
        Arguments:
            prop_registry -- the parent property Registry
            parent_prop_name -- the name of the parent property (used to notify 
            of value changes)
        """
        self.registry = prop_registry
        assert('notify_owner' in dir(self.registry))
        self.parent_prop_name = parent_prop_name
    
    def __setitem__(self, name, value):
        """Set a value in the table"""
        dict.__setitem__(self, name, value)
        self.registry.notify_owner(self.parent_prop_name)

    
class ChangeTable(XTable):
    """A dictionary of Physical Changes, where the name is the attribute to 
    change and value is the new attribute value"""
        
    
class ProgramTable(XTable):
    """A dictionary of Programs, designed by their names."""

    def __init__(self, prop_registry, parent_prop_name, schema):
        """Set the structure of the program's transforms
        
        schema is a list of tuple of the form (key, display_type, display_name)
        """
        XTable.__init__(self, prop_registry, parent_prop_name)
        self.program_keyword = schema

    def add_program(self, name, delay, prog_transform = None):
        """Add a program in the program Table."""
        prog = Program(self.registry, delay)
        #initialize transforms to default values
        for (transf_name, display) in self.program_keyword:
            prog.transform[transf_name] = Display.default_value[display.type](self.registry, self.parent_prop_name, [])
        if prog_transform and 'items' in dir(prog_transform):
            for (transf_name, transf_value) in prog_transform.items():
                if 'items' in dir(transf_value):
                    chg_table = ChangeTable(self.registry, self.parent_prop_name)
                    prog.transform[transf_name] = chg_table
                    for (chg_name, chg_value) in transf_value.items():
                        chg_table[chg_name] = chg_value
                else:
                    prog.transform[transf_name] = transf_value
        self[name] = prog
        
    
class Program():
    """A program represents a transformation to apply on a product, 
    and a transformation time. time can be either a numeric value, or
    a string containing a python expression that evaluate to a time. 
    This is usefull to model probability distribution such as function of the
    random module. These expressions should use the globally-defined random 
    number generator called rng (e.g. 'rng.expovariate(lambda=2)')
    
    A program is a particular form of property registry
    
    Attributes:
        transform -- a dictionary of program parameters
        time_law -- a python expression used to evaluate the delay (may be a float, int, or an expression calling random or rng) 
    """
    def __init__(self, prop_registry, time = 0.0):
        """Create a new instance of a Program
        
        Arguments:
            module -- the module the own the program.
            time -- the program duration (default = 0.0). It can be either a number, or an evaluable string. 
        """
        self.registry = prop_registry
        self.time_law = time
        self.transform = XTable(self.registry, 'program_table')
    
    def time(self, product = None):
        """Return the delay corresponding to this program. If time is a string
        expression, it is evaluated to a number.
        """
        return self.registry.eval_expression(self.time_law, product)

    def is_evaluable(self):
        """Return True if time_law is evaluable"""
        class DumbProduct:
            def __getitem__(self, value):
                return 1
        product = DumbProduct()
        try:
            eval_value = self.registry.eval_expression(self.time_law, product)
        except:
            logger.exception(_("could not evaluate expression {0}").format(self.time_law))
            return False
            
        if not type(eval_value) == str:
            return True
        else:
            return False
        
class Display:
    """
    
    display_name -- the localized name that should be used to display 
                            this property
            
            lower_bound --
            upper_bound -- 
    
    """

    REFERENCE = 1
    """A module present in the model, represented by its name"""
    VALUE = 2
    """Any (string) value"""
    BOOL_VALUE = 3
    """A boolean value"""
    INT = 4
    """A numerical value (int)"""
    FLOAT = 5
    """A numerical value (int)"""
    REFERENCE_LIST = 6
    """A list of references"""
    PROGRAM_TABLE = 7
    """A dictionary (ProgramTable) of emulica.emulation.Program, where keys are program names"""
    SETUP = 8
    """A emulica.emulation.SetupMatrix"""
    EVALUABLE = 9
    """A string that can be evaluated (using python's 'eval' function) to a numeric"""
    PHYSICAL_PROPERTIES_LIST = 10
    """a set of physical properties, and the associated value"""
    
    type_names = {REFERENCE: _("Module"),
                  VALUE: _("String"),
                  BOOL_VALUE: _("Boolean"),
                  INT: _("Integer"),
                  FLOAT: _("Float"),
                  REFERENCE_LIST: _("List of modules"),
                  PROGRAM_TABLE: _("Program table"),
                  SETUP: _("Setup table"),
                  EVALUABLE: _("Evaluable string"),
                  PHYSICAL_PROPERTIES_LIST: _("List of physical properties")}
    
    default_value = {REFERENCE: lambda reg, name, schema: None,
                     VALUE: lambda reg, name, schema: str(),
                     BOOL_VALUE: lambda reg, name, schema: bool(),
                     INT: lambda reg, name, schema: int(),
                     FLOAT: lambda reg, name, schema: float(),
                     REFERENCE_LIST: lambda reg, name, schema: list(),
                     PROGRAM_TABLE: lambda reg, name, schema: ProgramTable(reg, name, schema),
                     SETUP: lambda reg, name, schema: SetupMatrix(reg, 0, name),
                     EVALUABLE: lambda reg, name, schema: str(),
                     PHYSICAL_PROPERTIES_LIST: lambda reg, name, schema: ChangeTable(reg, name)}
                     
    
    def __init__(self, prop_type, display_name = None, lower_bound = 0, upper_bound = 2000000):
        """Create an new instance of a ModuleProperty
        
        Arguments:
            prop_type -- the type of the property : either one of the int 
                         constant defined in this module, or a string that is 
                         the name of the constant
            value -- the value of the property
            module -- the module tha this property belong to.
            
            
        """
        self.name = display_name
        if isinstance(prop_type, int):
            self.type = prop_type
        else:
            self.type = getattr(self, prop_type)
            #self.logger.warning("")
        self.lower = lower_bound
        self.upper = upper_bound

    def is_int(self):
        return self.type == self.INT
        
        
        


class PropertiesDialog(gtk.Dialog):
    """A window that shows modules properties.
    
    Attributes:
        window -- Gtk window 
        program_treeview -- GtkTreeview of the module's programs_table
        setup_treeview -- GtkTreeview of the module's setup matrix
        props_table - GtkTable, where to put label and entry to set properties other than program table and setup matrix
        name -- GtkEntry used to display/set module name
    """
    def __init__(self, parent, module, model, cmd_manager = None):
        """Create a new instance of a PropertiesWindow object
        
        Arguments:
            parent -- the parent window
            module -- the module which properties to show
            model -- the emulation model
            cmd_manager -- the undo/redo manager
            
        """
        gtk.Dialog.__init__(self, _("Properties of {0}").format(module.name),
                            parent,
                            gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.commands = cmd_manager
        self.properties = module.properties
        #add name-editing widget
        if 'name' in dir (module):
            hbox = gtk.HBox()
            label = gtk.Label(_("Module Name")+' :  ')
            label.set_alignment(1, 0.5)
            hbox.pack_start(label)
            name_entry = gtk.Entry()
            name_entry.set_text(module.name)
            hbox.pack_start(name_entry)
            def apply_change(entry):
                value = entry.get_text()
                if len(value) > 0:
                    self.commands.rename_module(module, value)
            name_entry.connect('changed', apply_change)
            hbox.set_border_width(5)
            self.vbox.pack_start(hbox, expand = False)
            self.vbox.pack_start(gtk.HSeparator(), expand = False)
            
        #add properties editing table
        self.props_table = PropertiesBox(model, 
                                    properties = module.properties, 
                                    cmd_manager = cmd_manager, 
                                    module = module)
        hbox = gtk.HBox()
        
        hbox.set_border_width(5)
        hbox.pack_start(self.props_table)
        self.vbox.pack_start(hbox)
        
        bbox = gtk.HButtonBox()
        bbox.set_property('layout-style', gtk.BUTTONBOX_END)
        bbox.set_border_width(5)
        add_button = gtk.Button(_("Add Property..."))
        
        self.action_area.pack_start(add_button)
        self.action_area.reorder_child(add_button, 0) 
        self.vbox.pack_start(bbox)
        
        add_button.connect('clicked', self.on_add_property_activate, module)
        self.connect('response', self.close)
        self.connect('delete-event', self.delete_event)
        self.show_all()
        
    def close(self, dialog, response):
        """Callbacks for destroying the dialog"""
        self.hide()
        
    def delete_event(self, dialog, event):
        """Callbacks for destroying the dialog"""
        return True
        
    def on_add_property_activate(self, button, module):
        """Called when the add property button is clicked: show an "add property dialog" and update the prop view"""
        dialog = gtk.Dialog(_("Add a new property to {0}").format(module.name),
                            self,
                            gtk.DIALOG_DESTROY_WITH_PARENT | gtk.DIALOG_MODAL,
                            (gtk.STOCK_ADD, gtk.RESPONSE_ACCEPT,
                             gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        table = gtk.Table(rows = 2, columns = 2)
        dialog.vbox.pack_start(table)
        #Get Name
        label_name = gtk.Label(_("Name:"))
        label_name.set_alignment(1, 0.5)
        label_name.set_padding(5, 0)
        entry_name = gtk.Entry()
        table.attach(label_name, 0, 1, 0, 1)
        table.attach(entry_name, 1, 2, 0, 1)
        #get Type
        label_type = gtk.Label(_("Type:"))
        label_type.set_alignment(1, 0.5)
        label_type.set_padding(5, 0)
        type_list = gtk.ListStore(int, str)
        for (name, num) in Display.type_names.items():
            type_list.append([name, num])
        combo_type = gtk.ComboBox(type_list)
        cell = gtk.CellRendererText()
        combo_type.pack_start(cell, True)
        combo_type.add_attribute(cell, 'text', 1)
        table.attach(label_type, 0, 1, 1, 2)
        table.attach(combo_type, 1, 2, 1, 2)
        
        dialog.show_all()
        
        if dialog.run() == gtk.RESPONSE_ACCEPT:
            #get name and type values
            new_name = entry_name.get_text()
            new_type = type_list[combo_type.get_active()][0]
            if new_name in module.properties.keys():
                pass
                #TODO: report error
            elif new_type < 0:
                pass
                #TODO: report error
            else:
                #everything ok, create and add prop
                self.properties.add_with_display(new_name, new_type)
                #update prop_box
                self.props_table.display_new_property(new_name, self.properties.get_display(new_name), self.properties[new_name])
                dialog.destroy()
        else:
            #close dialog
            dialog.destroy()
        
        
        

class PropertiesBox(gtk.Table):
    """A gtk Table that display a properties.Registry
    
    Attributes:
        
    """
    
    def __init__(self, model, prop_structure = None, properties = None, cmd_manager = None, module = None):
        """Create a new Instance of a basePropertiesBox
        
        Arguments:
            model -- the emulation model
            
        Keyword Arguments:
            prop_structure -- a list of (name, display) tupple
            properties -- the actual property object (optional if prop_structure
                          is given)
            cmd_manager -- the undo/redo manager
            module -- the module 
        """
        self.create_edit_widget = {Display.REFERENCE: self.__create_reference_edit_widget,
                                   Display.REFERENCE_LIST : self.__create_reference_list_edit_widget,
                                   Display.BOOL_VALUE: self.__create_bool_edit_widget,
                                   Display.INT: self.__create_num_edit_widget,
                                   Display.FLOAT: self.__create_num_edit_widget,
                                   Display.VALUE: self.__create_value_edit_widget,
                                   Display.PHYSICAL_PROPERTIES_LIST: self.__create_physicalprop_list_edit_widget,
                                   Display.SETUP: self.__create_setup_edit_widget,
                                   Display.EVALUABLE: self.__create_evaluable_edit_widget,
                                   Display.PROGRAM_TABLE: self.__create_program_table_edit_widget
                                  }
        
        if prop_structure is None:
            prop_structure = [(name, display) for (name, value, display) in properties.displayables()]
        
        self.module = module
        self.model = model
        self.commands = cmd_manager
        self.set_value_fn = dict()
        
        
        if len(prop_structure) != 0:
            gtk.Table.__init__(self, rows = len(prop_structure), columns = 2, homogeneous = False)
            self.row = 0
            for (name, display) in prop_structure:
                self.display_property(name, display)
        else:
            gtk.Table.__init__(self, rows = 1, columns = 2, homogeneous = False)
            label = gtk.Label()
            label.set_markup(_("<i>No properties to display</i>"))
            self.attach(label, 0, 2, 0, 1)
            
        if properties is not None:
            self.set_properties(properties)
    
    def display_property(self, name, display):
        """Add a new line in the inner Table to display the prop name."""
        (widget, set_value_fn) = self.create_edit_widget[display.type](name, display)
        widget.show_all()
        self.set_value_fn[name] = set_value_fn
        if display.type in [Display.PHYSICAL_PROPERTIES_LIST,
                         Display.REFERENCE_LIST]:
            #treeviews are displayed in a special manner...
            frame = gtk.Frame(display.name)
            widget.set_size_request(-1, 100)
            frame.add(widget)
            frame.show()
            self.attach(frame, 0, 2, self.row, self.row + 1, yoptions=gtk.EXPAND|gtk.FILL)
        else:
            label = gtk.Label(display.name+':')
            label.set_padding(5, 0)
            label.set_alignment(1, 0.5)
            label.show()
            self.attach(label, 0, 1, self.row, self.row + 1, yoptions=gtk.FILL)
            self.attach(widget, 1, 2, self.row, self.row + 1, yoptions=gtk.FILL)
        self.row += 1
        
        
    def display_new_property(self, new_name, new_display, new_value):
        """Display a newly added property"""
        self.resize(self.row + 1, 2)
        self.display_property(new_name, new_display)
        (set_value_fn, args) = self.set_value_fn[new_name]
        set_value_fn(new_value, *args)

    def set_properties(self, properties):
        """"""
        self.properties = properties
        for (name, (set_value_fn, args)) in self.set_value_fn.items():
            value = properties[name]
            set_value_fn(value, *args)
        

    def __set_prop_value(self, name, new_value):
        """Use the cmd_manager if it has been set"""
        if (self.commands != None and self.properties != None):
            self.commands.change_prop(self.properties, name, new_value)
        else:
            self.properties[name] = new_value
        

    def __create_value_edit_widget(self, name, display):
        """Return a gtk.Entry widget to display/set a VALUE property"""
        entry = gtk.Entry()
        def apply_change(entry, name):
            new_value = entry.get_text()
            self.__set_prop_value(name, new_value)
        def set_value(value, widget):
            widget.set_text(str(value))
        entry.connect('changed', apply_change, name)
        return (entry, (set_value, (entry,)))

    def __create_num_edit_widget(self, name, display):
        """Return a combination of a checkbox & spinbutton to display/set a 
        numeric property
        """
        hbox = gtk.HBox(False, 0)
        check = gtk.CheckButton()
        if display.is_int():
            i = 1.0
            d = 0
        else:
            i = 0.1
            d = 2
        spin = gtk.SpinButton(adjustment=gtk.Adjustment(lower = display.lower, 
                                                        upper = display.upper, 
                                                        step_incr = i),
                                                        digits = d)
        hbox.pack_start(check, expand = False)
        hbox.pack_start(spin, expand = True, fill = True)
        
        def on_check_toggled(toggle, spin):
            spin.set_sensitive(toggle.get_active())
        def apply_change(spin, name, is_int):
            if is_int:
                value = int(spin.get_value())
            else:
                value = spin.get_value()
            self.__set_prop_value(name, value)
        def set_value(value, spinb, checkb):
            if value == 0 :
                checkb.set_active(False)
                spinb.set_sensitive(False)
            else:
                spinb.set_value(value)
                checkb.set_active(True)
                
        spin.connect('changed', apply_change, name, display.is_int())
        check.connect('toggled', on_check_toggled, spin)
        return (hbox, (set_value, (spin, check)))

    def __create_bool_edit_widget(self, name, display):
        """Return a toggle button to display/set boolean properties"""
        check = gtk.CheckButton()
        def apply_change(check, name):
            new_value = check.get_active()
            self.__set_prop_value(name, new_value)
        def set_value(value, widget):
            widget.set_active(value)
        check.connect('toggled', apply_change, name)
        return (check, (set_value, (check,)))

    def __create_reference_edit_widget(self, name, display):
        """Return a combo box to display and set a module reference"""
        
        combo = gtk.combo_box_new_text()
        index = -1
        for ref in [m.fullname() for m in self.model.module_list() if m.__class__.__name__ == 'Holder']:
            combo.append_text(ref)
            index += 1
            
        def apply_change(combo, name):
            mod_name = combo.get_active_text()
            #TODO: sometime mod_name is None: what to do then ?
            new_value = self.model.get_module(mod_name)
            self.__set_prop_value(name, new_value)
        def set_value(value, widget):
            if value is None:
                combo.set_active(-1)
            else:
                mod = value
                if 'name' in dir(mod):
                    value = mod.fullname()
                else:
                    value = str()
                index = 0
                for row in widget.get_model():
                    if row[0] == value:
                        combo.set_active(index)
                    index += 1
        combo.connect('changed', apply_change, name)
        return (combo, (set_value, (combo,)))

    def __create_evaluable_edit_widget(self, name, display):
        """Return an entry to display/set an evaluable property (bg is yelllow
        if the text is not evaluable)
        """
        entry = gtk.Entry()
        def apply_change(entry, name):
            new_value = entry.get_text()
            self.__set_prop_value(name, new_value)
        def set_value(value, widget):
            widget.set_text(str(value))
        entry.connect('changed', apply_change, name)
        return (entry, (set_value, (entry,)))

    def __create_reference_list_edit_widget(self, name, display):
        """Return a treeview to display/set a list of references"""
        treeview = ReferenceListTreeView(self.model.modules, name, self.__set_prop_value, self.commands)
        sw = gtk.ScrolledWindow()
        sw.add(treeview)
        sw.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        return (sw, (treeview.set_value, ()))

    def __create_program_table_edit_widget(self, name, display):
        """Return a HBox that conatin a description label and an 'edit' button"""
        hbox = gtk.HBox()
        label = gtk.Label()
        label.set_alignment(0, 0.5)
        label.set_padding(5, 0)
        button = gtk.Button(_("Edit..."))
        def on_button_clicked(button, name):
            ProgramDialog(None, self.properties[name], self.model, self.commands)
        def set_value(value, widget):
            widget.set_text(_("{0:d} programs").format(len(value)))
            self.module.connect('property-changed', update_value, widget)
        def update_value(prop, module, widget):
            if prop == 'program_table':
                value = module.properties['program_table']
                widget.set_text(_("{0:d} programs").format(len(value)))
        button.connect('clicked', on_button_clicked, name)
        hbox.pack_start(label)
        hbox.pack_start(button)
        return (hbox, (set_value, (label,)))

    def __create_setup_edit_widget(self, name, display):
        """Return a HBox that contain a description label and an 'edit' button"""
        hbox = gtk.HBox()
        label = gtk.Label()
        label.set_alignment(0, 0.5)
        label.set_padding(5, 0)
        button = gtk.Button(_("Edit..."))
        def on_button_clicked(button, name):
            SetupDialog(None, self.properties[name], self.model, self.module, self.commands)
        def set_value(value, widget):
            widget.set_text(_("{0:d} programs").format(len(value)))
        button.connect('clicked', on_button_clicked, name)
        hbox.pack_start(label)
        hbox.pack_start(button)
        return (hbox, (set_value, (label,)))
        
    def __create_physicalprop_list_edit_widget(self, name, display):
        """Return a complex widget (based on a treeview) to display/add/remove 
        change list of physical properties changes
        """
        tree = PhysicalPropTreeView(self.commands)
        return (tree, (tree.set_value, ()))
        
        
class ReferenceListTreeView(gtk.TreeView):
    
    def __init__(self, modules, prop_name, set_val_fn, command_manager = None):
        self.cmd = command_manager
        self.model = gtk.ListStore(bool, str, object)
        self.prop_name = prop_name
        self.modules = modules
        self.set_value_fn = set_val_fn
        #self.selected = list()
        sorted_mod_list = modules.keys()
        sorted_mod_list.sort()
        for name in sorted_mod_list:
            if 'degrade' in dir(modules[name]):
                self.model.append((False, name, modules[name]))
        gtk.TreeView.__init__(self, self.model)
        self.set_property('headers-visible', False)
        #rendering as toggle for col 1
        col_cb_render = gtk.CellRendererToggle()
        col_cb_render.set_property('activatable', True)
        column = gtk.TreeViewColumn(None,  col_cb_render, active = 0)
        column.set_expand(True)
        self.append_column(column)
        col_cb_render.connect('toggled', self.on_check_toggled)
        #rendering as text for col 2
        render = gtk.CellRendererText()
        column = gtk.TreeViewColumn(None, render, text = 1)
        column.set_expand(True)
        self.append_column(column)
        
    def set_value(self, value):
        """Set the value of the reference list 
        value is a list of modules.
        """
        self.reference_list = value
        for i in range(len(self.model)):
            self.model[i][0] = (self.model[i][2] in value)
                
    def on_check_toggled(self, cell, path):
        module = self.model[path][2]
        if self.model[path][0]:
            self.reference_list.remove(module)
            self.model[path][0] = False
        else:
            self.reference_list.append(module)
            self.model[path][0] = True
        self.set_value_fn(self.prop_name, self.reference_list)
            
        
class PhysicalPropTreeView(gtk.TreeView):
        
    def __init__(self, command_manager = None):
        self.cmd = command_manager
        
        self.model = gtk.ListStore(str, str, bool)
        gtk.TreeView.__init__(self, self.model)
        #rendering column 1 as (simple) Entry
        col_name_render = gtk.CellRendererText()
        self.cell_renderer = col_name_render
        col_name_render.set_property('editable', True)
        column = gtk.TreeViewColumn('Name', col_name_render, text = 0)
        column.set_expand(True)
        self.append_column(column)
        col_name_render.connect('edited', self.apply_change_name) 
        
        #rendering column 2 as Entry, with validation
        col_delay_render = gtk.CellRendererText()
        col_delay_render.set_property('editable', True)
        col_delay_render.set_property("background", "yellow")
        column = gtk.TreeViewColumn('Value', col_delay_render, text = 1, background_set = 2)
        column.set_expand(True)
        self.append_column(column)
        col_delay_render.connect('edited', self.apply_change_value)
        self.connect('key-press-event', 
                     self.on_key_press_event, 
                     self.get_selection())
        self.connect('button-press-event', self.on_button_press_event)
        #self.set_size_request(-1, 75)
        
    def set_value(self, value):
        """"""
        self.model.clear()
        self.prop_dict = value
        for (name, value) in self.prop_dict.items():
            self.model.append([name, value, False])
        
    def on_key_press_event(self, widget, event, selection = None):
        """Callback connected to button-clicks. Delete selected row on Del key."""
        if event.type == gtk.gdk.KEY_PRESS and 'Delete' == gtk.gdk.keyval_name(event.keyval):
            #code adapted from pygtk faq
            model, treeiter, = selection.get_selected()
            if treeiter:
                path = model.get_path(treeiter)
                #remove row from program table
                (prog, ) = model.get(treeiter, 0)
                if self.cmd:
                    self.cmd.del_prop(self.prop_dict, prog)
                else:
                    del self.prop_dict[prog]
                model.remove(treeiter)
                selection.select_path(path)
                if not selection.path_is_selected(path):
                    row = path[0]-1
                    if row >= 0:
                        selection.select_path((row,)) 

    def on_button_press_event(self, widget, event):
        """Callback connected to mouse-click. Add a new row on double click."""
        if event.type == gtk.gdk._2BUTTON_PRESS:
            row = self.model.append()
            physical_prop_name = _("property{0}").format(self.model.get_string_from_iter(row))
            self.model.set(row, 0, physical_prop_name)
            self.model.set(row, 1, '0')
            if self.cmd:
                self.cmd.add_prop(self.prop_dict, physical_prop_name, 0)
            else:
                self.prop_dict[physical_prop_name] = 0
            
    def apply_change_name(self, cellrenderer, path, new_prop_name):
        """Callback connected to 'name' column. Change property name"""
        treeiter = self.model.get_iter_from_string(path)
        (old_prop_name, ) = self.model.get(treeiter, 0)
        if not old_prop_name == new_prop_name:
            text = self.prop_dict[old_prop_name]
            if self.cmd:
                self.cmd.change_prop_name(self.prop_dict, old_prop_name, new_prop_name)
            else:
                del self.prop_dict[old_prop_name]
                self.prop_dict[new_prop_name] = text
            self.model.set(treeiter, 0, new_prop_name)
        
    def apply_change_value(self, cellrenderer, path, new_text):
        """Callback connected to 'value' column. Change property value"""
        treeiter = self.model.get_iter_from_string(path)
        (physical_prop,) = self.model.get(treeiter, 0)
        if self.cmd:
            self.cmd.change_prop(self.prop_dict, physical_prop, new_text)
        else:
            self.prop_dict[physical_prop] = new_text
        
        self.model.set(treeiter, 2, True)#compute if the formula is correct...
        self.model.set(treeiter, 1, new_text)


class ProgramDialog(gtk.Dialog):
    """This class is used by PropertiesWindow to display and let the user edit the program table."""
    
    def __init__(self, parent, p_table, model, cmd_manager = None):
        gtk.Dialog.__init__(self, _("Edit program table"),
                            parent,
                            gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.program_table = p_table
        self.model = model
        self.cmd = cmd_manager
        
        #create the treeview
        treeview = self.__create_treeview()
        #create a big HBox
        hbox = gtk.HBox()
        self.vbox.add(hbox)
        #create a vbox into the hbox
        vbox = gtk.VBox()
        vbox.set_border_width(5)
        hbox.pack_start(vbox)
        #create a SW, put the treeview into it, add it to the vbox
        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add(treeview)
        vbox.pack_start(sw)
        #add a separator
        vbox.pack_start(gtk.HSeparator(), expand = False)
        #creates some buttons to add and remove the programs
        buttons = gtk.HButtonBox()
        buttons.set_border_width(5)
        new_button = gtk.Button(stock = gtk.STOCK_ADD)
        buttons.pack_start(new_button)
        del_button = gtk.Button(stock = gtk.STOCK_REMOVE)
        buttons.pack_start(del_button)
        vbox.pack_start(buttons, expand = False)
        #add a Vertical separator
        hbox.pack_start(gtk.VSeparator(), expand = False)
        #add a PropertyTable to the hbox
        self.propview = PropertiesBox(self.model,
                                      prop_structure = self.program_table.program_keyword,
                                      cmd_manager = self.cmd)
        vbox2 = gtk.VBox()
        vbox2.set_border_width(5)
        expand = False
        for (name, display) in self.program_table.program_keyword:
            expand = (display.type == Display.PHYSICAL_PROPERTIES_LIST)
            #True if there is only one physical ref
        vbox2.pack_start(self.propview, expand = expand)
        hbox.add(vbox2)
        #connect signals
        new_button.connect('clicked', self.on_new_button_clicked)
        del_button.connect('clicked', self.on_del_button_clicked, treeview.get_selection())
        treeview.connect('cursor_changed', self.on_treeview_cursor_changed, treeview.get_selection() )
        treeview.connect('key-press-event', self.on_key_press_event, treeview.get_selection())
        self.connect('response', self.close)
        self.connect('delete-event', self.delete_event)
        self.show_all()
        
    def close(self, dialog, response):
        """Callbacks for destroying the dialog"""
        self.hide()
        
    def delete_event(self, dialog, event):
        """Callbacks for destroying the dialog"""
        return True
        
    def __create_treeview(self):
        """Create treeview"""
        self.program_model = gtk.ListStore(str, str, bool)
        for (name, program) in self.program_table.items():
            row = [name, program.time_law, False]
            self.program_model.append(row)
        treeview = gtk.TreeView(self.program_model)
        treeview.set_size_request(-1, 150)
        #rendering column 1 as (simple) Entry
        col_name_render = gtk.CellRendererText()
        col_name_render.set_property('editable', True)
        column = gtk.TreeViewColumn('Program Name', col_name_render, text = 0)
        column.set_expand(True)
        treeview.append_column(column)
        col_name_render.connect('edited', self.apply_change_name) 
        #rendering column 2 as Text (may be a formula)
        col_delay_render = gtk.CellRendererText()
        col_delay_render.set_property('editable', True)
        col_delay_render.set_property("background", "yellow")
        column = gtk.TreeViewColumn('Delay', col_delay_render, text = 1, background_set = 2)
        column.set_expand(True)
        treeview.append_column(column)
        col_delay_render.connect('edited', self.apply_change_delay) 
        return treeview


    def __add_row(self):
        row = self.program_model.append()
        prog_name = _("program{0}").format(self.program_model.get_string_from_iter(row))
        delay = 0
        if self.cmd:
            self.cmd.add_prog(self.program_table, prog_name, delay, None)
        else:
            self.program_table.add_program(prog_name, 0)
        
        self.program_model.set(row, 0, prog_name)
        self.program_model.set(row, 1, str(delay))
        

    def __del_row(self, selection):
        #code adapted from pygtk faq
        model, treeiter, = selection.get_selected()
        if treeiter:
            path = model.get_path(treeiter)
            #remove row from program table
            (prog, ) = self.program_model.get(treeiter, 0)
            if self.cmd:
                self.cmd.del_prog(self.program_table, prog)
            else:
                del self.program_table[prog]
            
            model.remove(treeiter)
            # now that we removed the selection, play nice with 
            # the user and select the next item
            selection.select_path(path)
 
            # well, if there was no selection that meant the user
            # removed the last entry, so we try to select the 
            # last item
            if not selection.path_is_selected(path):
                row = path[0]-1
                # test case for empty lists
                if row >= 0:
                    selection.select_path((row,))

    def on_treeview_cursor_changed(self, treeview, selection):
        """Called when the cursor position change in the treeview; Get selected 
        row, and display corresponding program's properties."""
        model, treeiter, = selection.get_selected()
        if treeiter:
            path = model.get_path(treeiter)
            #remove row from program table
            (name, ) = self.program_model.get(treeiter, 0)
            prog = self.program_table[name]
            self.propview.set_properties(prog.transform)
        
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
    
    def apply_change_name(self, cellrenderer, path, new_text):
        """Callback connected to 'name' column.Change program name"""
        treeiter = self.program_model.get_iter_from_string(path)
        (prog, ) = self.program_model.get(treeiter, 0)
        logging.info(_("changing program {name} to {new_name}").format(name = prog, new_name = new_text))
        if not self.program_table.has_key(new_text):
            if self.cmd:
                self.cmd.change_prog_name(self.program_table, prog, new_text)
            else:
                self.program_table[new_text]= self.program_table[prog]
                del self.program_table[prog]
            self.program_model.set(treeiter, 0, new_text)

    def apply_change_delay(self, cellrenderer, path, new_text):
        """Callback connected to 'delay' column. Change program's delay"""
        treeiter = self.program_model.get_iter_from_string(path)
        (prog,) = self.program_model.get(treeiter, 0)
        if self.cmd:
            self.cmd.change_prog_time(self.program_table[prog], new_text)
        else:
            self.program_table[prog].time_law = new_text    
        self.program_model.set(treeiter, 2, not self.program_table[prog].is_evaluable())
        self.program_model.set(treeiter, 1, new_text)


class SetupDialog(gtk.Dialog):
    """This class is used by PropertiesWindow to display and let the user edit the setup table."""
    
    def __init__(self, parent, setup_table, model, module, cmd_manager = None):
        """Create an new instance of a SetupDialog."""
        gtk.Dialog.__init__(self, _("Edit Setup Matrix"),
                            parent,
                            gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
        self.setup_table = setup_table
        self.cmd = cmd_manager
        self.setup_model = gtk.ListStore(str, str, str)
        program_model = gtk.ListStore(str)
        for p in module.properties['program_table'].keys():
            program_model.append([p])
        self.setup_default_spin = gtk.SpinButton(digits = 1, 
                                                 adjustment = gtk.Adjustment(value = float(self.setup_table.default_time), 
                                                                             lower = 0., 
                                                                             upper = 10000., 
                                                                             step_incr = 1.))
        self.setup_default_spin.connect('changed', self.apply_change)
        for row in self.setup_table.items():
            self.setup_model.append(row)
        self.treeview = gtk.TreeView(self.setup_model)
        self.treeview.connect('key-press-event', self.on_key_pressed_event, self.treeview.get_selection())
        self.treeview.connect('button-press-event', self.on_button_press_event)
        
        default_time_box = gtk.HBox()
        default_time_box.pack_start(gtk.Label(_("Default setup time:")))
        default_time_box.pack_start(self.setup_default_spin)
        self.vbox.pack_start(default_time_box, expand = False)
        self.vbox.pack_start(self.treeview)
        
        
        #rendering as combo for col 1
        col_init_render = gtk.CellRendererCombo()
        col_init_render.set_property('editable',True)
        col_init_render.set_property('text-column', 0)
        col_init_render.set_property('model', program_model)
        column = gtk.TreeViewColumn('Initial', col_init_render, text = 0)
        column.set_expand(True)
        self.treeview.append_column(column)
        col_init_render.connect('edited', self.apply_change_init)

        #rendering as combo for col 2
        col_final_render = gtk.CellRendererCombo()
        col_final_render.set_property('editable',True)
        col_final_render.set_property('text-column', 0)
        col_final_render.set_property('model', program_model)
        column = gtk.TreeViewColumn('Final', col_final_render, text = 1)
        column.set_expand(True)
        self.treeview.append_column(column)
        col_final_render.connect("edited", self.apply_change_final)

        #rendering with spin for col 3
        spin_cell_render = gtk.CellRendererSpin()
        spin_cell_render.set_property('editable', True)
        spin_cell_render.set_property('digits', 1)
        adjust = gtk.Adjustment(lower = 0, step_incr = 0.1, page_incr = 1, upper = 10000)
        spin_cell_render.set_property('adjustment', adjust)
        column = gtk.TreeViewColumn('Delay', spin_cell_render, text = 2)
        column.set_expand(True)
        self.treeview.append_column(column)
        spin_cell_render.connect('edited', self.apply_change_delay)
        self.connect('response', self.close)
        self.connect('delete-event', self.delete_event)
        self.show_all()
        
    def close(self, dialog, response):
        """Callbacks for destroying the dialog"""
        self.hide()
        
    def delete_event(self, dialog, event):
        """Callbacks for destroying the dialog"""
        return True

    def on_button_press_event(self, widget, event):
        """Callback connected to mouse-click. Add a new row on double click."""
        if event.type == gtk.gdk._2BUTTON_PRESS:
            row = (_("initial"), _("final"), '0')
            self.setup_model.append(row)
            if self.cmd:
                self.cmd.add_setup(self.setup_table, row[0], row[1], 0.0)
            else:
                self.setup_table.add(row[0], row[1], 0.0)
    

    def on_key_pressed_event(self, widget, event, selection):
        """Callback connected to button-clicks. Delete selected row on Del key."""
        if event.type == gtk.gdk.KEY_PRESS and 'Delete' == gtk.gdk.keyval_name(event.keyval):
            #code adapted from pygtk faq
            
            (model, treeiter,) = selection.get_selected()
            if treeiter:
                path = model.get_path(treeiter)
                #remove row from program table
                (init, final) = model.get(treeiter, 0, 1)
                #TODO: remove setup
                if self.cmd:
                    self.cmd.del_setup(self.setup_table, self.init, final)
                else:
                    self.setup_table.remove(init, final)
                model.remove(treeiter)
                # now that we removed the selection, play nice with 
                # the user and select the next item
                selection.select_path(path)

                # well, if there was no selection that meant the user
                # removed the last entry, so we try to select the 
                # last item
                if not selection.path_is_selected(path):
                    row = path[0]-1
                    # test case for empty lists
                    if row >= 0:
                        selection.select_path((row,))

    def apply_change_init(self, cellrenderertext, path, new_text):
        """Callback connected to combos in 'initial' column. Change initial setup value"""
        treeiter = self.setup_model.get_iter_from_string(path)
        (initial, final) = self.setup_model.get(treeiter, 0, 1)
        if self.cmd:
            self.cmd.change_setup(self.setup_table, initial, final, new_initial = new_text)
        else:
            self.setup_table.modify(initial, final, new_initial = new_text)
        self.setup_model.set(treeiter, 0, new_text)

    def apply_change_final(self, cellrenderertext, path, new_text):
        """Callback connected to combos in 'final' column. Change final setup value"""
        treeiter = self.setup_model.get_iter_from_string(path)
        (initial, final) = self.setup_model.get(treeiter, 0, 1)
        if self.cmd:
            self.cmd.change_setup(self.setup_table, initial, final, new_final = new_text)
        else:
            self.setup_table.modify(initial, final, new_final = new_text)
        self.setup_model.set(treeiter, 1, new_text)

    def apply_change_delay(self, cellrenderer, path, new_text):
        """Callback connected to combos in 'delay' column. Change setup delay"""
        treeiter = self.setup_model.get_iter_from_string(path)
        (initial, final) = self.setup_model.get(treeiter, 0, 1)
        time = locale.atof(new_text)
        if self.cmd:
            self.cmd.change_setup(self.setup_table, initial, final, new_time = time)
        else:
            self.setup_table.modify(initial, final, new_time = time)
        self.setup_model.set(treeiter, 2, new_text)

    def apply_change(self, spin):
        """Callback connected to the default setup value spin. Update value in setup table."""
        value = spin.get_value()
        self.setup_table.default_value = value  


