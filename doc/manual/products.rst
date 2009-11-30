
Products
========

Products are the physical object on which actuators apply 
transformations. They are also the source of data used by observers. 
Products are identified in the model by a unique identifier
(usually a positive integer), called PID, or Product-ID. 

Products record the various kind of transformations they go through: 
life-cycle event such as creation and disposal, the sequence of shape or 
space transformation (i.e. programs) that have been applied, and the sequence 
of assembly and disassembly applied.

History
    It is important to record every step in the life-cycle of products,
    because the nature of a finished product depends of the kind of transformation
    applied, and also of their order. Furthermore, in an experiment aiming at
    verifying traceability features of a control system, the product history may
    be used as a mean of comparison.  
    
Creation and disposal
    Creation time is recorded in the 'create_time' attribute of class Product.
    Likewise, the time of disposal is recorded in the 'dispose_time' attribute. 
    Before product's disposal, this attribute is zero. When 
    emulation stops, all products are disposed.
    
Shape transformation
    Shape transformations are recorded in the attribute 'shape_history'.
    This attribute is a list of tuples, each one representing a transformation.
    
    These tuple have four elements:
        * the time of the transformation begining,
        * the time of the transformation end,
        * the name of the actuator doing the transformation,
        * the name of the program being executed.
            
Space transformation
    Space transformation are recorded in the attribute 'space_history'.
    This attribute is a list of tuples, each one representing a position change of
    the product. These tuple have two elements:
    * the time of arrival of the product in a position
    * the position: either the name of a Holder, or the name of a space actuator.
    
    The sequence of position is continuous: if a product is in position P1 
    at t=2 and in position P2 at t=5 (no other position change being 
    recorded between t=2 and t=5) we can assume that it was in position P1 
    from t=2 to t=5. 
    
Assembly/Disassembly
    TODO
        
        
Physical Properties
-------------------
    Products have physical properties, such as their mass, length, or any 
    other property useful to make the model work. Physical properties are 
    implemented as items of the class Product. So if p is Product, p['prop'] is the
    property 'prop' of p.
        
    Initialization
        These properties are initialized by create actuators, using the 
        'physical-properties' keyword (in the how field of the creation request). 
        This key must point to a dictionary of the form key:'property name', value: 
        'property value'. 
        
    Modification of physical properties
        Physical properties of products are modified by Shape Actuator (by 
        definition of what shape actuators are). The list of modification is passed
        to the acturator using the 'change' field of the program that is executed. 
        This key must point to a dictionary of change statements, in the form key:
        'property name', value: 'new property value'.
        
    Getting product physical properties
        The physical properties of the product being transformed can be used 
        in the program delay, using the statement "product['property-name']". This 
        statement is evaluated when running the program according to the current 
        value of the product physical attribute. Likewise, this statement can be 
        used when assigning a new value to a physical property 
        So, "Program({'change': {'length': "product['length']-1"}}, "product['mass']")")",
        is a program that decrement the physical property 'length', with a delay equal
        with the product mass.
        
    Properties bound to other properties
        Properties can be set as a function of other properties. To access 
        another property in the evaluation context of a property, the statement 
        self['propname'] shall be used. For example, the property 'density' can be 
        defined as "self['mass'] / self['volume']". When the property is accessed, 
        its value is computed. Circular references must be avoided, and cannot at 
        the moment been detected.
        
    
    Agregation and Composition of products
        TODO
