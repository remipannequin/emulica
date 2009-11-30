Properties
==========

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
