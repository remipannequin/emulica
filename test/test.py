#! /usr/bin/python
# *-* coding: utf8 *-*

"""
Run the whole test suite
"""
import logging
from xml.dom import minidom
import sys
sys.path.insert(0,"../src/")

console = logging.StreamHandler()
logging.getLogger().setLevel(logging.WARNING)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def main(func_list):
    failed = []
    for test in [eval(testname) for testname in func_list if testname.startswith('test_')]:
        for r in test():
            print "%s... %s" % r
            if not r[1]:
                failed.append(r[0])
        
    print "========================"
    if len(failed) > 0:
        
        print "failed tests:"
        for test in failed:
            print " * %s" % test
    else:
        print "all tests passed"

def test_sim1():
    import sim1  as sim
    model = sim.create_model()
    sim.start(model)
    result = [(pid, 
               p.shape_history, 
               p.space_history, 
               p.create_time, 
               p.dispose_time) for (pid, p) in model.products.items()]
    yield ("sim1", result == sim.exp_result)

        
def test_sim2():
    import sim2 as sim
    model = sim.create_model()
    sim.start(model)
    result_product = [(pid, p.shape_history, 
                       p.space_history, 
                       p.create_time, 
                       p.dispose_time) for (pid, p) in model.products.items()]
    result_resource = model.modules["space1"].trace
    yield ("sim2: product", result_product == sim.exp_result_product)
    yield ("sim2: resource", result_resource == sim.exp_result_resource)


def test_sim3():
    import sim3 as sim
    model = sim.create_model()
    sim.start(model)
    result_product = [(pid, p.shape_history, 
                       p.space_history, 
                       p.create_time, 
                       p.dispose_time) for (pid, p) in model.products.items()]
    result_resource = [model.modules["transporter"].trace, model.modules["machine"].trace] 
    #print result_product
    yield ("sim3: product", result_product == sim.exp_result_product)
    yield ("sim3: resource", result_resource == sim.exp_result_resource)

    
def test_sim4():
    import sim4 as sim
    model = sim.create_model()
    sim.start(model)
    result_product = [(pid, p.shape_history, 
                       p.space_history, 
                       p.create_time, 
                       p.dispose_time) for (pid, p) in model.products.items()]
    result_resource = [model.modules["transporter"].trace, model.modules["machine"].trace]
    #print result_product, result_resource
   
    yield ("sim4: product", result_product == sim.exp_result_product)
    yield ("sim4: resource", result_resource == sim.exp_result_resource)


def test_sim5():
    import sim5 as sim
    model = sim.create_model()
    sim.start(model)
    result = [(pid, 
               p.shape_history, 
               p.space_history, 
               p.create_time, 
               p.dispose_time) for (pid, p) in model.products.items()]
    yield ("sim5", result == sim.exp_result)

def test_sim6():
    import sim6 as sim
    (l1, t1, m) = sim.run(1, 1, 123456)
    (l2, t2, m) = sim.run(1, 1, 123456)
    result = (t1 == t2) and (l1 == l2)
    if not result:
        if t1 != t2:
            print [(t1[i], t2[i]) for i in range(len(t1))]
            
        if l1 != l2:
            pass
            #print l1, l2
            
    (l1, t1, m) = sim.run(1.2, 1, 8750)
    (l2, t2, m) = sim.run(1.2, 1, 8750)
    result = result and (t1 == t2) and  (l1 == l2)
    
    yield ("sim6: RNG, same seeds give same traces", result)
    
    (l3, t3, m) = sim.run(1, 1, 480972)
    result = (l3 != l2) and (t2 != t3)
    
    
    yield ("sim6: RNG different seeds give different traces", result)
    
    
    
    
def test_sim7():
    import sim7 as sim
    model = sim.create_model()
    sim.start(model)
    result_product = [(pid, p.shape_history, 
                       p.space_history,
                       p.create_time,
                       p.dispose_time) for (pid, p) in model.products.items()]
    result_resource = [model.modules["transporter"].trace, model.modules["machine"].trace]
    #print result_product, result_resource
    yield ("sim7: product", result_product == sim.exp_result_product)
    yield ("sim7: resource", result_resource == sim.exp_result_resource)


def test_sim8():
    import sim8  as sim
    sim.pos_list = []
    model = sim.create_model()
    sim.start(model)
    result = [(pid, 
               p.shape_history, 
               p.space_history, 
               p.create_time, 
               p.dispose_time) for (pid, p) in model.products.items()]
    yield ("sim8: product", result == sim.exp_result)
    yield ("sim8: observation", compare_positions(sim.pos_list, sim.exp_result_position))

def test_sim10():
    import sim10 as sim
    model = sim.create_model()
    sim.start(model)
    result_product = [(pid, 
                       p.shape_history, 
                       p.space_history, 
                       p.create_time, 
                       p.dispose_time) for (pid, p) in model.products.items()]
    result_resource = [model.modules["trans"].trace, model.modules["assy"].trace]
    #print result_product, sim.exp_result_product
    yield ("sim10: product", result_product == sim.exp_result_product)
    yield ("sim10: resource", result_resource == sim.exp_result_resource)

def test_sim11():
    import sim11 as sim
    model = sim.create_model()
    sim.start(model)
    result = [(pid, 
               p.shape_history, 
               p.space_history, 
               p.create_time, 
               p.dispose_time) for (pid, p) in model.products.items()]
    yield ("sim11", result == sim.exp_result)


def test_sim13():
    import sim13 as sim
    model = sim.create_model()
    sim.start(model)
    result = sim.report_list
    #print result, sim.exp_report_list
    if len(result) == len(sim.exp_report_list):
        yield ("sim13 (attach_report_socket)", reduce(lambda x, y: x and y, map(compare_report, result, sim.exp_report_list)))
    else:
        print "compared reports list size mismatch"
        yield ("sim13 (attach_report_socket)", False)

def test_sim14():
    import sim14 as sim
    model = sim.create_model()
    sim.start(model)
    result_product = [(pid, 
                       p.shape_history, 
                       p.space_history,
                       dict([(key, p[key]) for key in p.properties.keys()]),
                       p.create_time, 
                       p.dispose_time) for (pid, p) in model.products.items()]
    result_resource = [model.modules["transporter"].trace, model.modules["machine"].trace]
    #print result_product
    yield ("sim14 (physical properties): product", result_product == sim.exp_result_product)
    yield ("sim14 (physical properties): resource", result_resource == sim.exp_result_resource)

def test_sim15():
    import sim15 as sim
    model = sim.create_model()
    sim.start(model)
    result_product = [(pid, 
                       p.shape_history, 
                       p.space_history,
                       p.create_time, 
                       p.dispose_time) for (pid, p) in model.products.items()]
    result_resource = [model.get_module("cell.transporter").trace, model.get_module("cell.machine").trace]
    #print result_product
    yield ("sim15 (basic composite modelling 1): product", result_product == sim.exp_result_product)
    yield ("sim15 (basic composite modelling 1): resource", result_resource == sim.exp_result_resource)

def test_sim16():
    import sim15 as sim
    model = sim.create_model()
    sim.start(model)
    result_product = [(pid, 
                       p.shape_history, 
                       p.space_history,
                       p.create_time, 
                       p.dispose_time) for (pid, p) in model.products.items()]
    result_resource = [model.get_module("cell.transporter").trace, model.get_module("cell.machine").trace]
    #print result_product
    yield ("sim16 (composite modelling, submodel properties): product", result_product == sim.exp_result_product)
    yield ("sim16 (composite modelling, submodel properties): resource", result_resource == sim.exp_result_resource)


def test_config1():
    """test emuML with create dispose, holder and push observer"""
    import sim1 as sim
    from emulica import emuML, emulation
    
    m1 = sim.create_model()
    efile = emuML.EmulationWriter(m1)
    output = efile.write()
    f = open("sim1.xml",'r')
    exp_output = f.read()
    f.close()
    yield ("config: sim1, save", compare_dom(output, exp_output))
    
    m2 = emuML.load("sim1.xml")
    output = emuML.save(m2)
    yield ("config: sim1, load and save", compare_dom(output, exp_output))
    
    m3 = emuML.load("sim1.xml")
    sim.initialize_control(m3)
    sim.start(m3)
    
    result = [(pid, 
               p.shape_history, 
               p.space_history, 
               p.create_time, 
               p.dispose_time) for (pid, p) in m3.products.items()]
    yield ("config: sim1, execute", result == sim.exp_result)
    
def test_config2():
    """test emuML with create, space, shape, pushobserver"""
    import sim4 as sim
    from emulica import emuML
    m1 = sim.create_model()
    output = emuML.save(m1)
    #test whether output equals sim4.xml...
    f = open("sim4.xml",'r')
    exp_output = f.read()
    f.close()
    yield ("config: sim4, save", compare_dom(output, exp_output))
    m2 = emuML.load("sim4.xml")
    output = emuML.save(m2)
    yield ("config: sim4, load and save", compare_dom(output, exp_output))
    m3 = emuML.load("sim4.xml")
    sim.initialize_control(m3)
    sim.start(m3)
    result_product = [(pid, p.shape_history, 
                       p.space_history, 
                       p.create_time, 
                       p.dispose_time) for (pid, p) in m3.products.items()]
    result_resource = [m3.modules["transporter"].trace, m3.modules["machine"].trace]
    #print result_product, sim.exp_result_product
    yield ("config: sim4, execute (product)", result_product == sim.exp_result_product)
    yield ("config: sim4, execute (resource)", result_resource == sim.exp_result_resource)

def test_config3():
    """test emuML with create, holder, pushobserver, failure"""
    import sim7 as sim
    from emulica import emuML
    m1 = sim.create_model()
    output = emuML.save(m1)
    #test whether output equals sim4.xml...
    f = open("sim7.xml",'r')
    exp_output = f.read()
    f.close()
    yield ("config: sim7, save", compare_dom(output, exp_output))
    m2 = emuML.load("sim7.xml")
    output = emuML.save(m2)
    yield ("config: sim7, load and save", compare_dom(output, exp_output))
    m3 = emuML.load("sim7.xml")
    sim.initialize_control(m3)
    sim.start(m3)
    result_product = [(pid, p.shape_history, 
                       p.space_history, 
                       p.create_time, 
                       p.dispose_time) for (pid, p) in m3.products.items()]
    result_resource = [m3.modules["transporter"].trace, m3.modules["machine"].trace]
    #print result_product, sim.exp_result_product
    yield ("config: sim7, execute (product)", result_product == sim.exp_result_product)
    yield ("config: sim7, execute (resource)", result_resource == sim.exp_result_resource)

def test_config4():
    """test emuML with create, holder with speed and capacity, pushobserver, pullobserver"""
    import sim8 as sim
    from emulica import emuML
    m1 = sim.create_model()
    output = emuML.save(m1)
    #test whether output equals sim4.xml...
    f = open("sim8.xml",'r')
    exp_output = f.read()
    f.close()
    yield ("config: sim8, save", compare_dom(output, exp_output))
    m2 = emuML.load("sim8.xml")
    output = emuML.save(m2)
    yield ("config: sim8, load and save", compare_dom(output, exp_output))
    m3 = emuML.load("sim8.xml")
    sim.initialize_control(m3)
    sim.start(m3)
    result = [(pid, 
               p.shape_history, 
               p.space_history, 
               p.create_time, 
               p.dispose_time) for (pid, p) in m3.products.items()]
    yield ("config: sim8, execute (product)", result == sim.exp_result)
    yield ("config: sim8, execute (observation)", sim.pos_list == sim.exp_result_position)

def test_config5():
    """Test emuML with physical properties"""
    import sim14 as sim
    from emulica import emuML
    m1 = sim.create_model()
    output = emuML.save(m1)
    f = open("sim14.xml",'r')
    exp_output = f.read()
    f.close()
    yield ("config: sim14, save", compare_dom(output, exp_output))
    m2 = emuML.load("sim14.xml")
    output = emuML.save(m2)
    yield ("config: sim14, load and save", compare_dom(output, exp_output))
    m3 = emuML.load("sim14.xml")
    sim.initialize_control(m3)
    sim.start(m3)
    result = [(pid, 
               p.shape_history, 
               p.space_history,
               dict([(key, p[key]) for key in p.properties.keys()]),
               p.create_time, 
               p.dispose_time) for (pid, p) in m3.products.items()]
    result_resource = [m3.modules["transporter"].trace, m3.modules["machine"].trace]
    yield ("config: sim14, execute (product)", result == sim.exp_result_product)
    yield ("config: sim14, execute (resources)", result_resource == sim.exp_result_resource)

def test_config6():
    import sim15 as sim
    from emulica import emuML
    m1 = sim.create_model()
    
    output = emuML.save(m1)
    f = open("sim15.xml",'r')
    exp_output = f.read()
    f.close()
    
    #there is one xml doc on each line
    yield ("config: sim15, save (main)", compare_dom(output, exp_output))
    
    m3 = emuML.load("sim15.xml")
    #sim.initialize_control_submodel(m3.modules['cell'])
    sim.initialize_control(m3)
    sim.start(m3)
    result = [(pid, 
               p.shape_history, 
               p.space_history,
               p.create_time, 
               p.dispose_time) for (pid, p) in m3.products.items()]
    result_resource = [m3.get_module("cell.transporter").trace, m3.get_module("cell.machine").trace]
    yield ("config: sim15, execute (product)", result == sim.exp_result_product)
    yield ("config: sim15, execute (resources)", result_resource == sim.exp_result_resource)

    
def test_write_message():
    """test write message"""
    from emulica import emuML
    from emulica.emulation import Report, Request
    instance = Report("source", "event", "location", date = 24, comment = "comment", params = {'p1': 2, 'p2': 40, 'p': 1.567})
    exp_result = """<report><who>source</who><what>event</what><when>24</when><where>location</where><how><element name="p1">2</element><element name="p2">40</element><element name="p">1.567</element></how><why>comment</why></report>"""
    result = emuML.write_report(instance)
    yield ("emuML: write report", compare_dom(result, exp_result))

def test_parse_message():
    """test parse message""" 
    from emulica import emuML
    from emulica.emulation import Report, Request
    message = """<request><who>actor</who><what>an action</what><when>15</when><where>location</where><how><element name="p">1.74957</element><element name="pa">7</element><element name="p9">ab</element></how><why>comment</why></request>"""
    exp_result = Request("actor", "an action", "location", date = 15, comment = "comment", params = {'p': 1.74957, 'pa': 7, 'p9': "ab"})
    result = emuML.parse_request(message)
    yield ("emuML: parse request (full request)", compare_report(result, exp_result))
    message = """<request><who>actor</who><what>an action</what><where>location</where></request>"""
    exp_result = Request("actor", "an action", "location")
    result = emuML.parse_request(message)
    yield ("emuML: parse request (minimal request)", compare_report(result, exp_result))
    message = """<request><who>actor</who><where>location</where></request>"""
    try:
        result = emuML.parse_request(message)
        r = False
    except emuML.EmuMLError:
        r = True
    yield ("emuML: parse request (exception if missing fields)", r)
    message = """<request><who>actor</who><what>an action</what><where>location</where><when>albert</when></request>"""
    try:
        result = emuML.parse_request(message)
        r = False
    except emuML.EmuMLError:
        r = True
    yield ("emuML: parse request (exception on date format)", r)

def test_replace_prop():
    """Test partial evaluation of properties affectation"""
    #TODO
    from emulica import emulation, properties
    model = emulation.Model()
    product = emulation.Product(model)
    product['p1'] = 1
    product['prop2'] = 2
    r = True
    #TODO: include random numbers
    test_list = [('p1', "product['p1']", 1),
                 ('p2', "product['prop2']", 2),
                 ('p3', "product['prop2'] + product['p1']", 3)]
                 #('p4', "p1", 1), 
                 #('p5', "p1 + product['p1']", 2),
                 #('p6', "p1 + product['prop2'] + product['p1'] + prop2", "self['p1'] + 2 + 1 + self['prop2']")]
    model = emulation.Model()
    registry = properties.Registry(model, None)

    for (name, test, result) in test_list:
        registry[name] = test
        
    for (p_name, test, exp_result) in test_list:
        result = registry.evaluate(p_name, product)
        r = (r and result == exp_result)
        print "{0} evaluates to {1}".format(test, result)
        if not r:
            print test
    yield ("evaluation of physical  property", r)

def test_plot_process_trace():
    from emulica import plot 
    tests = [([(0.0, 1.0, 'p1'), (1.0, 2.0, 'p1')],
              [(0.0, 2.0, 'p1')]),
             ([(0.0, 1.0, 'p1'), (1.0, 2.0, 'p1'), (2.0, 3.0, 'p2')], 
              [(0.0, 2.0, 'p1'), (2.0, 3.0, 'p2')]),
             ([(0.0, 1.0, 'p1'), (1.0, 2.0, 'p1'), (4.0, 5.0, 'p2')], 
              [(0.0, 2.0, 'p1'), (4.0, 5.0, 'p2')]),
             ([(0.0, 1.0, 'p1'), (1.0, 2.0, 'p1'), (4.0, 5.0, 'p2'), (6.0, 7.0, 'p2')], 
              [(0.0, 2.0, 'p1'), (4.0, 5.0, 'p2'), (6.0, 7.0, 'p2')]),
             ([(0.0, 1.0, 'p1'), (1.0, 2.0, 'p1'), (3.0, 3.0, 'setup'), (4.0, 5.0, 'p2'), (6.0, 7.0, 'p2')], 
              [(0.0, 2.0, 'p1'), (4.0, 5.0, 'p2'), (6.0, 7.0, 'p2')]),
            ]
    r = True
    chart = plot.GanttChart()
    for (input, exp_result) in tests:
        (result, failure) = chart.process_trace(input)
        r = r and result == exp_result
        if not r:
            print result, exp_result
    yield ("plot: process_trace", r)
    
def test_command_manager():
    from emulica import emulation, properties
    from emulica.emulicapp.modelling import CommandManager
    import sim14 as sim
    model = sim.create_model()
    
    r = True
    cmd = CommandManager()
    #verify the can undo and can redo return false
    r = (r and (cmd.can_undo() == False))
    r = (r and (cmd.can_redo() == False))
    yield("command manager: initialisation", r)
    
    r = True
    cmd.create_module('test_module', emulation.CreateAct, model)
    #verify that the module has been created
    module = model.modules['test_module']
    r = (r and (module != None) and (module.__class__.__name__ == 'CreateAct'))
    r = (r and (cmd.can_undo() == True))
    r = (r and (cmd.can_redo() == False))
    cmd.undo()
    r = (r and (not 'test_module' in model.modules.keys()))
    r = (r and (cmd.can_undo() == False))
    r = (r and (cmd.can_redo() == True))
    cmd.redo()
    module2 = model.modules['test_module']
    r = (r and (module == module2))
    r = (r and (cmd.can_undo() == True))
    r = (r and (cmd.can_redo() == False))
    yield("command manager: create_module", r)
    
    r = True
    cmd.rename_module(module, 'test_module2')
    module3 = model.modules['test_module2']
    r = (r and (module3 == module))
    r = (r and (module3.name == 'test_module2'))
    r = (r and (not 'test_module' in model.modules.keys()))
    r = (r and ('test_module2' in model.modules.keys()))
    cmd.undo()
    r = (r and ('test_module' in model.modules.keys()))
    r = (r and (not 'test_module2' in model.modules.keys()))
    r = (r and (module3.name == 'test_module'))
    cmd.redo()
    r = (r and (not 'test_module' in model.modules.keys()))
    r = (r and ('test_module2' in model.modules.keys()))
    r = (r and (module3.name == 'test_module2'))
    yield("command manager: rename_module", r)
    
    r = True
    cmd.delete_module(module, model)
    #verify module has been deleted
    r = (r and (not 'test_module2' in model.modules.keys()))
    cmd.undo()
    r = (r and ('test_module2' in model.modules.keys()))
    cmd.redo()
    r = (r and (not 'test_module2' in model.modules.keys()))
    yield("command manager: delete_module", r)
    
    r = True
    create = model.modules['create']
    source = model.modules['source']
    sink = model.modules['sink']
    cmd.change_prop(create.properties, 'destination', sink)
    r = (r and (create.properties['destination'] == sink))
    cmd.undo()
    r = (r and (create.properties['destination'] == source))
    cmd.redo()
    r = (r and (create.properties['destination'] == sink))
    yield("command manager: change property", r)
    
    r = True
    machine = model.modules['machine']
    cmd.add_prog(machine.properties['program_table'], 'p4', 4, {'change': {'length': 1}})
    r = (r and ('p4' in machine.properties['program_table']))
    p = machine.properties['program_table']['p4']
    
    
    
    r = (r and (machine.properties['program_table']['p4'] == p))
    cmd.undo()
    r = (r and (not 'p4' in machine.properties['program_table']))
    cmd.redo()
    r = (r and ('p4' in machine.properties['program_table']))
    r = (r and (machine.properties['program_table']['p4'] == p))
    yield("command manager: add program", r)
    
    r = True
    cmd.change_prog_time(p, 12)
    r = (r and (p.time() == 12))
    if not r: print "do failed"
    cmd.undo()
    r = (r and (p.time() == 4))
    if not r: print "undo failed"
    cmd.redo()
    r = (r and (p.time() == 12))
    if not r: print "redo failed"
    yield("command manager: change program", r)
    
    r = True
    cmd.change_prog_name(machine.properties['program_table'], 'p4', 'p4bis')
    r = (r and ('p4bis' in machine.properties['program_table']))
    r = (r and (not 'p4' in machine.properties['program_table']))
    r = (r and (machine.properties['program_table']['p4bis'] == p))
    cmd.undo()
    r = (r and (not 'p4bis' in machine.properties['program_table']))
    r = (r and ('p4' in machine.properties['program_table']))
    r = (r and (machine.properties['program_table']['p4'] == p))
    cmd.redo()
    r = (r and ('p4bis' in machine.properties['program_table']))
    r = (r and (not 'p4' in machine.properties['program_table']))
    r = (r and (machine.properties['program_table']['p4bis'] == p))
    yield("command manager: change program name", r)
    
    r = True
    cmd.del_prog(machine.properties['program_table'], 'p4bis')
    r = (r and (not 'p4bis' in machine.properties['program_table']))
    cmd.undo()
    r = (r and ('p4bis' in machine.properties['program_table']))
    r = (r and (machine.properties['program_table']['p4bis'] == p))
    cmd.redo()
    r = (r and (not 'p4' in machine.properties['program_table']))
    yield("command manager: remove program time", r)
    
    r = True
    p1 = machine.properties['program_table']['p1']
    p2 = machine.properties['program_table']['p2']
    m = machine.properties['setup']
    cmd.add_setup(m, p1, p2, 3)
    r = (r and (m.get(p1, p2) == 3))
    cmd.undo()
    r = (r and (m.get(p1, p2) == 1))
    cmd.redo()
    r = (r and (m.get(p1, p2) == 3))
    yield("command manager: add setup", r)
    
    r = True
    cmd.change_setup(m, p1, p2, new_time = 5)
    r = (r and (m.get(p1, p2) == 5))
    cmd.undo()
    r = (r and (m.get(p1, p2) == 3))
    cmd.redo()
    r = (r and (m.get(p1, p2) == 5))
    yield("command manager: change setup", r)
    
    r = True
    cmd.del_setup(m, p1, p2)
    r = (r and (m.get(p1, p2) == 1))
    cmd.undo()
    r = (r and (m.get(p1, p2) == 5))
    cmd.redo()
    r = (r and (m.get(p1, p2) == 1))
    yield("command manager: remove setup", r)
    
    
    
    
#def compare_trace(tr1, tr2):
#    n = len(tr1) 
#    if not len(tr2) == n:
#        print "trace don't have the same number of elements"
#        return false
#    r = True
#    for i in range(n):
#        r = r and tr1[i][2] == tr2[i][2]
#        r = r and (tr1[i][1] - tr2[i][1]) <= pow(10, -6)
#        r = r and (tr1[i][0] - tr2[i][0]) <= pow(10, -6)
#        if not r:
#            print tr1[i], tr2[i]
#            return False
#    return r

def compare_report(r1, r2):
    result = True
    for i in ['who', 'what', 'when', 'where', 'how', 'why']:
        result = result and (getattr(r1, i) == getattr(r2, i))
        if not result: 
            print "attribute %s, %s != %s"%(i, getattr(r1, i), getattr(r2, i))
            return result
    return result

def compare_positions(l1, l2):
    """l1 or l2 is a list or tuple (float, dict), where dict is position=>pid"""
    if len(l1) != len(l2):
        print "sequence have not the same lenght", len(l1), len(l2)
        return False
    for i in range(len(l1)):
        
        if not l1[i][0] == l2[i][0]:
            print "not the instants are observed"
            return False
        t = l1[i][0]
        d1 = l1[i][1]
        d2 = l1[i][1]
        if not len(d1) == len(d2):
            print "not the same number of product at {O}".format(t)
            return False
        for (k, v) in d1.items():
            if not k in d2.keys():
                print "not the same sequence: different position"
                print d1, d2
            if not v == d1[k]:
                print "not the same sequence: different products"
                print d1, d2
    return True
    
    

def compare_dom(s1, s2):
    """Util for emuML tests"""    
    dom1 = minidom.parseString(s1)
    dom2 = minidom.parseString(s2)
    dom1.normalize()
    dom2.normalize()
    
    return compare_node(dom1, dom2)

def compare_node(dom1, dom2):
    """test if two DOM are "equivalent" 'ie have the same tree structure, regardless of the order of siblings
    """
    def node_cmp(n1, n2): 
        node_id1 = n1.nodeName
        if 'getAttribute' in dir(n1) and n1.hasAttribute('name'):
            node_id1 += n1.getAttribute('name')
        node_id2 = n2.nodeName
        if 'getAttribute' in dir(n2) and n2.hasAttribute('name'):
            node_id2 += n2.getAttribute('name')
        return cmp(node_id1, node_id2)
        
    if not dom1.nodeType == dom2.nodeType:
        print dom1.nodeType, dom2.nodeType
        print dom1.toxml()
        print dom2.toxml()
        return False
    if not dom1.nodeName == dom2.nodeName: 
        print dom1.nodeName, dom2.nodeName
        print dom1.toxml()
        print dom2.toxml()
        return False
    if dom1.nodeValue == None:
        if not dom1.nodeValue == dom2.nodeValue:
            print dom1.nodeValue, dom2.nodeValue
            print dom1.toxml()
            print dom2.toxml()
            return False
    else:
        if not dom1.nodeValue.strip() == dom2.nodeValue.strip(): 
            print dom1.nodeValue.strip(), dom2.nodeValue.strip()
            return False
    l1 = sorted(dom1.childNodes, node_cmp)
    l2 = sorted(dom2.childNodes, node_cmp)
    if not len(l1) == len(l2):
        print "number of childs:", len(l1), len(l2)
        print dom1.toxml()
        print dom2.toxml()
        return False
    test = True
    for i in range(len(l1)):
        test = test and compare_node(l1[i],l2[i])
    return test

def test_holderstate():
    from emulica import emulation as emu
    h = emu.Holder(emu.Model(), "h", speed = 0)
    
    #test instanciate
    instance = emu.HolderState(h)
    r =  0 == len(instance)
    r = r and instance.is_first_ready() == False
    r = r and instance.product_list() == []
    yield ("holderstate: instantiation", r)

    #test append
    instance = emu.HolderState(h)
    instance.append(1)
    r = len(instance) == 1
    r = r and instance.is_first_ready() == True
    r = r and instance.product_list() == [1]
    instance = emu.HolderState(h)
    for i in range(10):
        instance.append(i)
    r = r and len(instance) == 10
    r = r and instance.is_first_ready() == True
    r = r and instance.product_list() == range(10)
    yield ("holderstate: append", r)
    
    #test pop
    instance = emu.HolderState(h)
    for i in range(10):
        instance.append(i)
    r = r and instance.product_list() == range(10)
    instance.pop()
    r = r and instance.product_list() == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    instance.append(10)
    for i in range(5):
        instance.pop()
    r = r and instance.product_list() == [6, 7, 8 , 9, 10]
    yield ("holderstate: pop", r)
    
    #test update_pos
    instance = emu.HolderState(h)
    for i in range(10):
        instance.append(i)
    instance.update_positions()
    r = r and len(instance) == 10
    r = r and instance.is_first_ready() == True
    r = r and instance.product_list() == range(10)
    yield ("holderstate: update position", r)

def test_setupmatrix():
    from emulica.properties import SetupMatrix, Registry
    from emulica import emulation
    model = emulation.Model()
    p = emulation.Product(model)
    m = SetupMatrix(Registry(p, model.rng), 3)

    def test(init, final, expRes):
        t = m.get(init, final)
        if t == expRes:
            return True
        else:
            print t, expRes
            return False
        
    m.add('p1', 'p2', 1)
    v = test('p1', 'p2', 1)
    m.add('p1', 'p3', 2)
    v *= test('p1', 'p3', 2)
    v *= test('p0', 'p0', 0)
    v *= test('p0', 'p1', 3)
    m.add('p2', 'p3', 4)
    v *= test('p2', 'p3', 4)
    v *= test('p1', 'p2', 1)
    v *= test('p1', 'p3', 2)
    m.add('p3', 'p1', 5)
    v *= test('p3', 'p1', 5)
    yield ("setup matrix (adding values)", bool(v))

    v = True
    m = SetupMatrix(Registry(p, model.rng), 3)
    m.add('p3', 'p1', 5)
    m.modify('p3', 'p1', new_final = 'p12')
    v *= test('p3', 'p12', 5)
    m.add('p2', 'p3', 4)
    m.modify('p2', 'p3', new_initial = 'p12')
    v *= test('p12', 'p3', 4)
    m.add('p1', 'p2', 1)
    m.modify('p1', 'p2', new_time = 2)
    v *= test('p1', 'p2', 2)
    yield ("setup matrix (modifying values)", bool(v))
    

if __name__ == '__main__': main(dir())


