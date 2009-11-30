Emulica File Format
===================

This file describe the file format used for emulica:

A emulica file is a ZIP archive, containing three files:

#. emulation.xml: an XML file as defined in emuML.dtd

#. props.db: a dictionnary of properties, marshalled using pickle
    list of keys/ values:
     * layout -- a dictionary that associate module name with the module position in the canvas (as a tuple (x,y))
     * exec -- a dictionary that give execution parameter such as execution mode, emulation time limit, etc...

#. control.py 
    a python source file that contain the control processes. 
    It must define a method called 'initialize_control' taking the emulation 
    model as argument. This method must return a list of tuple composed of 
    Process instances and of their process execution method.

The file may have the extension '.emu' and the mime type "application/x-emulica"



EmuML XML Syntax
-----------------
:: 

    emulation
        |
        +-interface [1]
        |   |
        |   +-input [*]
        |
        +-modules [1]
            |
            +-submodel [*]
            |
            +-module [*]
                |
                +-property (name, type) [*]
                    |
                    +-VALUE [*]
 
Property types:
 * common simple types: `string`, `int`, `double`, `boolean`
 * custom simple types: `reference`
 * complex types: `program-table`, `setup-table`, `change-table`
   We use the word table to design both dictionary- and list-like types
 
 
Simple type use a simple parser (that take the type as argument) while each complex types use it own parser.

VALUE can be either value (for common simple types), reference, or one of the complex type. If there is more
than one VALUE element under a property element, a list is created. If there is no VALUE element, None is used.

Simple VALUE::
   
   value (type)
   
   reference
   
Complex VALUE::
   
    value-list
         |
         +-VALUE
   
    program-table (schema)
        |
        + -program (name, delay) [1..*]
            |
            + -transform (name, type) [*]
                |
                +-VALUE

    setup-table (default-delay)
        |
        +-setup (initial, final, delay) [*]
        
    change-table
        |
        +- change [*]
            |
            +- VALUE

NB: attribute schema is a coma-separated sequence of the keyword `source` destination`, `change`, enclosed in square brackets. For instance `[source, destination]` for a Space Actuation programs, or `[change]` for a Shape Actuation programs.


 




    
