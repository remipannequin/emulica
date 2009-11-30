Composite Modeling
==================

The goal is to apply the composite design pattern to modelling.


Rationale:
----------

    Some systems include control routine. For instance, in the tracilog assembly 
    cell, the PLC manage both a space transformation( station loading and unloading)
    and a shape transformation (station operation). Therefore, a set of modules must
    be able to receive Requests and to send Reports. Therefore, a new module: 
    submodel must be included.

    This feature will also simply modelling of complex systems. For instance, in the
    'manufacturing' example, each cell can be represented as a submodel which 
    includes its own control routine. Thus, we will be able to create some bigger
    modelling components to change the modelling granularity (in particular in case 
    of routing/scheduling studies).


Implementation:
---------------

    So, a :class:`Model` is a :class:`Module`, and can be added in another model. 
    When a submodel is added to a model, all (or some, see below) the modules of 
    the submodel are declared is the super model. As a model is a Module, a 
    model must have a name. By convention, the default name for the top-level 
    model is 'main'.

    As a Model is a Module, it has its own Report and Request queue... The Report 
    and Request sent to a submodel may be processed by a SimPy.Simulation.Process 
    instance, that is named by convention ModuleProcess, and that must be registered
    as a control process.

    A public/private property might be added to Module, in order to determine if a module
    in a submodel is visible in the super model. (ie added in its 'modules' dictionary)
    By default, modules in submodels should be visibles, because its the only way to
    interact between composed and composite models (for instance, some holders and 
    observers must be public). However, some module should be private, to avoid 
    potential conflict. This is not critical, through, because we can choose to 
    trust the modeller.


Integration in gseme:
---------------------

Graphical representation:
-------------------------



Tests:
------

Two tests can be set up:
1) two actuators (shape and space) and a holder associated with the shapeAct are
bundled into a submodel, with a ModuleProcess class. On request, the submodel 
sequencialy loads the operation space, setup the shape actuator, run the 
program, and unload the operation space. The main model create and dispose 
products, sends requests to the submodel.

2) a submodel represent a manufacturing cell. (like in sim4). The sub model has
a control process, that is triggered by product arrival in the input buffer.
The main model create and dispose products.
