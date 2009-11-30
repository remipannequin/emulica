Emulation Modules
=================

Emulation modules are classified in three categories:
 * `Actuators`_ (i.e. controlable physical transformation of products and resources)
 * (uncontrolable) `Physical processes`_ (products holder, failures, etc...)
 * `Observers`_

Actuators
---------

.. autoclass: emulica.emulation.Actuator



Create
^^^^^^

    The create actuator (seme.emulation.CreateAct) creates new products and put them 
    into a holder.
    When emulation begins, the create actuator wait for requests to arrive 
    on its request_socket. When a request arrives, it verify that the requested action
    is 'create', and create a new product. If the request's date is in the future, the actuator
    waits until the emulation time is greater or equal than the request date (NB: the 
    request in the module's request socket must be sorted in chronological order). The product creation
    is done accroding to the parameter 'productType' and 'pid' of the request. 
    Default value are used if the parameters are missing. The newly ccreated product is 
    finally put into the 'destination' Holder, and a report ('create-done') is sent in the
    module's report socket.
    
    **Properties:**
        *destination*
            the Holder where to put the created product
        *product_prop*
            a list of physical properties that the created product will have
        
    **Action keywords (what):**
        *create*
            request the creation of a product
        *create-done*
            report the creation of a product

    **Action parameters (how):**
        *PID*
                the identifiant of the new product(by default, the smaller 
                free PID is chosen).
        *productType*
                the type of product to create (by default, 'defaultType').
        *physical-properties*
                a dictionary of physical properties to initialize for the 
                created product.

    Instanciation of a create actuator::    
        
        model = emulation.Model()
        h = emulation.Holder(model, "holder1")
        c = emulation.CreateAct(model, "create1", h)

    Simple control of a create actuator:: 
       
        class ControlCreate(emulation.Process):
            """Simple Simpy Process to control the create actuator"""
            def run(self, modules):
                """Process execution method"""
                createModule = modules["create1"]
                m = emulation.Request("create1", "create")
                yield emulation.put, self, createModule.request_socket, [m]

    Control of a create actuator, using creation date and 
    physical properties:: 
          
        class ControlCreate(Process):
            """Simpy Process to control the create actuator"""
            def run(self, model):
                """Process execution method"""
                createModule = model.modules["create"]
                request_list = []
                r = Request("create", "create", date=2
                            params={'productType':"P_heavy", 
                                    'physical-properties': {'mass':12, 'length': 5}}))
                request_list.append(r)
                r = Request("create", "create", date=10
                            params={'productType':"P_light", 
                                    'physical-properties': {'mass':2, 'length': 5}}))
                request_list.append(r)
                r = Request("create", "create", date=10
                            params={'productType':"P_small", 
                                    'physical-properties': {'mass':2, 'length': 0.1}}))
                request_list.append(r)
                yield put, self, createModule.request_socket, request_list
        
    
    
Dispose
^^^^^^^

    The dispose actuator (seme.emulation.DisposeAct) disposes the 
    first product of a holder.
    When emulation begins, the dispose actuator waits for requests to arrive 
    on its request socket. When a request arrives, it verify that the requested action
    is 'dispose', fetch a product from the 'source' holder, and mark it as 
    disposed (by calling the product's dispose() method). If the request's date is in the future, the actuator
    waits until the emulation time is greater or equal than the request date (NB: the 
    request in the module's request socket must be sorted in chronological order).
    Finally, a report ('dispose-done') is sent in the module's report socket.
        
    **Properties:**
        *source*
            the holder where to take the product to dispose.
    
    **Action keywords (what):**
        *dispose*
            request to dispose a product.
        *dispose-done*
            report that a product has been disposed
            
    Instanciation of a Dispose actuator::
            
        model = emulation.Model()
        h = emulation.Holder(model, "holder1")
        d = emulation.DisposeAct(model, "dispose1", h)
            
Shape
^^^^^

    A Shape Actuator (:class:`seme.emulation.ShapeAct`) changes a set of 
    physical attributes of a product.
    A Shape actuator is associated with a Holder (its transformation holder),
    where products reside during their transformation (NB: a Shape Actuator 
    cannot load/ unload product to/from its transformation holder, a Space 
    actuator is required to do that). 
    
    **Properties:**
        *program_table*
            A dictionary of available programs (i.e. program that can be run by this actuator).          |
        *setup*
            A :class:`SetupMatrix` instance, that is used to compute setup delays.
        *holder* 
            The :class:`Holder` where the transformation is done.        |
       
    **Program parameters:**
        *change*
            A dictionary of physical properties affectation. Keys are 
            physical properties names, values are affectation to this 
            properties.
        
    
    **Action keywords (what):**
        *setup*
            request a program change.
        *make*
            request execution of the current program.
        *setup-done*
            report that a setup has been done.
        *busy*
            report that the actuator is now busy.
        *idle*
            report that the actuator is now idle.
    
    **Action parameters (how):**
        *program*
            The name of the program to set up (when associated with the 
            'setup' action). If the action is 'make', an implicit setup is
            done if nessecary (i.e. if the current program is not the 
            requested program).
        
    Instanciation and initialization of a Shape actuator::
            
        model = Model()
        espaceMachine = Holder(model, "espaceMachine")
        machine = ShapeAct(model, "machine", espaceMachine)
        machine['program_table']['p1'] = Program(None, 4)
        machine['program_table']['p2'] = Program(None, 5)
        machine['program_table']['p3'] = Program(None, 6)
        m = SetupMatrix(1)
        m.add('p1','p3',2)
        m.add('p3','p1',3)
        machine['setup'] = m
            
    
Space
^^^^^
    A Space actuator (seme.emulation.SpaceAct) change the position of
    a product. The move is done according to the keys 'source' and 
    'destination' of the programs, that point to Holders. During its 
    production cycle, this actuator fetch the first product of the 'source' 
    holder, and after the program delay, put it in the destination Holder. 
    The position change is recorded by the product, as well as being in the
    Space actuator.
    
    **Properties:**
        *program_table*
            A dictionary of available programs (i.e. program that can be run
            by this actuator).
        *setup*
            A SetupMatrix instance, that is used to compute setup delays.
        
    **Program parameters:**
        *source*
            A holder from where the products are taken.
        
        *destination*
            A holder to where the product are put.
        
    **Action keywords (what):**
        *setup*
            Request a program change.
        *move*
            Request execution of the current program.
        *setup-done*
            Report that a setup has been done.
        *busy*
            Report that the actuator is now busy.
        *idle*
            Report that the actuator is now idle.
        
    **Action parameters (how):**
        *program*
            The name of the program to set up (when associated with the 
            'setup' action). If the action is 'make', an implicit setup is
            done if nessecary (i.e. if the current program is not the 
            requested program).
        
    Instanciation of a Space actuator::
            
        model = Model()
        source = Holder(model, "source")
        sink = Holder(model, "sink")
        espaceMachine = Holder(model, "espaceMachine")

        sp = SpaceAct(model, "transporter")
        sp['program_table']['load'] = Program({'source':source, 
                                               'destination':espaceMachine}, 2)
        sp['program_table']['unload'] = Program({'source':espaceMachine, 
                                                 'destination':sink}, 2)
            

Assemble
^^^^^^^^

    An assemble actuator assemble a product taken from a 'source'
    holder, with the product currently present in an assembly holder.
    The incoming product is added as a component of the product that is in 
    the assembly holder. Note that this actuator cannot load or unload the 
    product in the assembly holder: it must be explicitly moved or created 
    into the holder, and moved from the holder after transformation.
    
    **Properties:**
        *program_table*
            A dictionary of available programs (i.e. program that can be run
            by this actuator).
        *setup*
            A SetupMatrix instance, that is used to compute setup delays.
        *holder*
            The holder in which the assembly is made.
        
    **Program parameters:**
        *source*
            A holder from where the product are taken.
        
    **Action keywords (what):**
        *setup*
            Request a program change.
        *assemble*
            Request execution of the current program.
        *setup-done*
            Report that a setup has been done.
        *busy*
            Report that the actuator is now busy.
        *idle*
            Report that the actuator is now idle.
    
    **Action parameters (how):**
        *program*
            The name of the program to set up (when associated with the 
            'setup' action). If the action is 'make', an implicit setup is
            done if nessecary (i.e. if the current program is not the 
            requested program).
        
        
    Instanciation of a Assemble actuator:: 
            
        model = emulation.Model()
        source1 = emulation.Holder(model, "source1")
        source2 = emulation.Holder(model, "source2")
        assy_space = emulation.Holder(model, "assy_space")
        assy = emulation.AssembleAct(model, "assy", assy_holder = assy_space)
        assy['program_table']['p1'] = emulation.Program({'source':source2}, 5)
        assy['program_table']['p2'] = emulation.Program({'source':source1}, 3)
            
    
Disassemble
^^^^^^^^^^^

    A disassemble actuator take a product, and decompose it into 
    two products: one that stay in the disassembly holder, while the other
    one is put the 'destination' holder.
    
    **Properties:**
        *program_table*
            A dictionary of available programs (i.e. program that can be run
            by this actuator).
        *setup*
            A SetupMatrix instance, that is used to compute setup delays.
        *holder*
            The holder in which the disassembly is made.
        
    **Program parameters:**
        *destination*
            A holder from where the disassembled products are put.
        
    **Action keywords (what):**
        *setup*
            request a program change.
        *disassemble*
            request execution of the current program.
        *setup-done*
            report that a setup has been done.
        *busy*
            report that the actuator is now busy.
        *idle*
            report that the actuator is now idle.
        
    **Action parameters (how):**
        *program*
            The name of the program to set up (when associated with the 
            'setup' action). If the action is 'make', an implicit setup is
            done if nessecary (i.e. if the current program is not the 
            requested program).
    
    Instanciation of a Disassemble actuator
        


Physical Processes
------------------

Failure
^^^^^^^
A failure is an event that happen after mtbf units of time, and that modify the performance of one or sevaral actuators during mttr units of times. Then the failure can be repeated. The mtbf and mttr parameters can be strings that uses the 'rng' token, as an instance of the model's random number generator. For instance 'rng.expovariate(1/20)' is a valid expression, that is evaluated
each time the failure enters the 'wait mtbf' state.


There are two type of failures: complete or partial (performance degradation)

If the failure is complete, the resource supporting the actuation process is preempted, and released after mttr. The operation interrupted is resumed.
For example, if a complete failure of duration 5 happen at t=2, while the actuator is processing a task of lenght 10 that have begun at t=0, the actuator is reported failed from t=2 to t=7, and then resume its processing from t=7 to t=15 (8 time unit remain)


If the failure is partial, a capacity modification is applied during a period that correspond to the mttr. The capacity modification is a positive number usualy comprised between 0 and 1, that is substracted to the resource capactity.
For exemple, if applying a capacity degradation of 0.3 (30%) on an initial capacity of 1, results in a capacity of 0.7.
When the capacity is degraded, the actuator is interrupted; the remaining time is evaluated (on the basis of a normal (i.e. 100%) capacity), and the waiting_time is avaluated according to the new capacity:
new_time = remaining_time / new_capacity
When the capcity is restored, a similar operation is done.

    **Properties:**
        *mtbf*
            the expression the give the mean time before failure
        *mttr*
            the expression the give the mean time to repair
        *degradation*
            the degradation ratio (between 0 and 1) (optional, default value is 1)
        *repeat*
            True is the failure repeats

    **Action keywords (what):**
        *failure-begin*
            report that the failure begin
        *failure-end*
            report that the failure process ends

    **Action parameters (how):**
        *mttr* 
            the actual value of the failure
        *degradation*
            the degradation of the failure (1 if the failure is total)

Holder
^^^^^^

    a Holder contains products. It is associated with a place where products 
    can be, for instance an inventory or the iner space of a machine of station.
    A Holder can contains several products, and behave like a simple FIFO queue.
    Space and create actuators can put product into an holder. The new product 
    is added at the end of the queue. Space and dispose actuators can take a 
    product from a holder, the taken product is the one in the front of the queue.
    
    **Properties:**
        *capacity*
            The maximum number of product that can be put in a holder. A null 
            value means an infinite capacity.
        
        *speed*
            The speed determine how uch time a product takes to change position
            inside the holder. For instance, it take 4 units of time to go 
            through a holder with capacity 2 and speed 0.5. A null value means 
            an infinite speed. 
            
        
    Instanciation of a Holder::
            
        h = emulation.Holder(model, "holder1")
        h['capacity'] = 4
        h['speed'] = 1
            

Observers
---------

PushObserver
^^^^^^^^^^^^

    A Push Observer returns information on product. When a product is ready in 
    the observed holder (i.e. the first product of the holder can be get), the 
    module send a Report. The report attributes depends of the module 
    properties. The reports are pushed into the control system.
    
    **Properties:**
        *holder*
            The holder where the products to observe are.
        *event_name*
            The name of the event that is generated when a product is observed.
        *observe_type*
            Observe product type. If true, the observer report the type of the observed product.
        *identify*
            Identify products. If true, the observer report the pid of the observed product.
    
    Report parameters (how)
        *productType*
            The type of the observed product. Used only if property observe_type is True.
        *productID*
            The PID of the obersed product. Used only if property identify is True.
            
    Instanciation of a PushObserver::
            
        obs1 = emulation.PushObserver(model, "observer1", "ev1", observe_type = False, holder = h)
            
    
PullObserver
^^^^^^^^^^^^



    
   
