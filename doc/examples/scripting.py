#! /usr/bin/python
# *-* coding: utf8 *-*

import sys
#use devel version
sys.path.insert(0, '../../src')

import gtk
from emulica import emulation, plot
from emulica.emulation import Process, put, get, Report, Request, Store

from math import ceil




class Schedule(list):
    """This class represent the tasks (Lot) that must be executed by the shop floor."""

    class Lot:
        def __init__(self, product_type, quantity, final_dest):
            self.product_type = product_type
            self.quantity = quantity
            assert(quantity != 0)
            self.quantity_done_sf = 0
            self.final_dest = final_dest
            self.quantity_done_f = 0

        def report_done_sf(self):
            """Increment the qty done, and return True if the Lot is finished"""    
            self.quantity_done_sf += 1
            return self.finished_sf()
            
        def report_done_f(self):
            """Increment the qty done, and return True if the Lot is finished"""    
            self.quantity_done_f += 1
            return self.finished_f()
        
        def finished_sf(self):
            return self.quantity_done_sf >= self.quantity
        
        def finished_f(self):
            return self.quantity_done_f >= self.quantity
        
    def __init__(self):
        list.__init__(self)
        self.sf_current = 0
        self.f_current = {'a': -1, 'b': -1, 'c': -1}
        
    def update_f_current(self):
        """Set the cursor for final routing"""
        for i in range(len(self)):
            lot = self[i]
            if not lot.finished_f():
                if self.f_current[lot.final_dest] == -1:#not already affected
                    self.f_current[lot.final_dest] = i
            
        
    def append_lot(self, product_type, quantity, final_dest):
        self.append(Schedule.Lot(product_type, quantity, final_dest))
    
    def sf_get_next(self):
        """Return the type of the next product to do in SF cell"""
        assert(not self.sf_finished())
        return self[self.sf_current].product_type
            
    def sf_report_done(self):
        """increment the qty done of the current SF lot"""
        if self[self.sf_current].report_done_sf():
            self.sf_current += 1
            
    def sf_finished(self):
        """Return True if all the Lots have been proceced in SF"""
        return self.sf_current >= len(self)
    
    
    def routable(self, p_type):
        """Return True if p_type can be routed: ie if p_type is one of the current lot"""
        for dest in['a', 'b', 'c']:
            if self[self.f_current[dest]].product_type == p_type:
                return True
        return False
    
    def route(self, p_type):
        """Return the destination where to route p_type"""
        for dest in['a', 'b', 'c']:
            if self.f_current[dest] != -1:
                if self[self.f_current[dest]].product_type == p_type:
                    return dest
        
    
    def report_routed(self, p_type, dest):
        """Report that a product has been sent to dest. Update todo and route."""
        assert(self[self.f_current[dest]].product_type == p_type)
        if self[self.f_current[dest]].report_done_f():
            #if finished, search a new one to make
            self.f_current[dest] = -1
            self.update_f_current()
    

class CellControl(Process):
    """Control a production cell production is set up according to product type"""
    def run(self, model, cellname):
        self.name = cellname
        inObs = model.modules["obs_in"+self.name]
        inObs_report = inObs.create_report_socket(multiple_observation = True)
        workObs = model.modules["obs_work"+self.name]
        workObs_report = workObs.create_report_socket()
        trans = model.modules["load"+self.name]
        machine = model.modules["machine"+self.name]
        machine_report = machine.create_report_socket()
        while True:
            ##attente de l'arrivée d'un pièce
            yield get, self, inObs_report, 1
            ev = self.got[0]
            rq = Request("load"+self.name,"move",params={'program':'load'})
            yield put, self, trans.request_socket, [rq]
            ##pièce prête
            yield get, self, workObs_report, 1
            ev = self.got[0]
            ##get program from product type
            p = ev.how['productType']
            yield put, self, machine.request_socket, [Request(self.name,"setup", params={"program":"p"+str(p)})]
            ##début process
            yield put, self, machine.request_socket, [Request(self.name,"make")]
            ##attente fin process
            fin = False
            while not fin:
                yield get, self, machine_report, 1
                fin = self.got[0].what=="idle"
            ##déchargement
            yield put, self, trans.request_socket, [Request("load"+self.name, "move", params={"program":'unload'})]

class DetectFailure(Process):
    """Detect failure on a cell"""
    def run(self, model, schedule):
        failure = model.get_module('fail1')
        rp_failure = failure.create_report_socket()
        while True:
            yield get, self, rp_failure, 1
            state = self.got[0].what
            if state == 'failure-begin':
                print "failure detected"
                #TODO: change schedule 
    

class ControlSt(Process):
    """Control how to route products into inventory St"""
    def run(self, model):
        outObs_report = model.modules["obs_outSf"].create_report_socket()
        trans = model.modules["transSt"]
        while True:
            yield get, self, outObs_report, 1
            ev = self.got[0]
            p = ev.how['productType']
            yield put, self, trans.request_socket, [Request("transSt", "move", params={'program': "load_st"+str(p)})]


class ControlF(Process):
    """Control how to route product from inventory St to F{a,b,c} production cells"""
    def run(self, model, sched = Schedule()):
        """observe inventory holders, and input buffers, act on """
        
        product_registry = []
        trans = model.modules["transSt"]
        report_hub = Store()
        for i in range(1, 13):
            model.modules['obs_st'+str(i)].attach_report_socket(report_hub)
        trans.attach_report_socket(report_hub)
        
        #sp : dict p_type -> number of products in st
        st = [False, False, False, False, False, False, False, False, False, False, False, False,]
        while True:
            rq = None
            yield get, self, report_hub, 1
            rp = self.got[0]
            if 'productType' in rp.how:
                #event from a product obs
                p_type = rp.how['productType']
                
                #a product p_type just arrived or a transfert just finished
                #dest taken from route
                if sched.routable(p_type):
                    dest = sched.route(p_type)
                    
                    rq = Request('transSt', 'move', params = {'program': 'unload_%sto%s' % (rp.where, dest)})
                    yield put, self, trans.request_socket, [rq]
                    sched.report_routed(p_type, dest)
                else:
                    print "memo"
                    st[p_type] = True
            else:
                #trans op finished
                for p_type in [ptype for ptype in range(12) if st[ptype]]:
                    #for each product type in store
                    if sched.routable(p_type):
                        print st
                        dest = sched.route(p_type)
                        
                        rq = Request('transSt', 'move', params = {'program': 'unload_st%sto%s' % (p_type, dest)})
                        yield put, self, trans.request_socket, [rq]
                        sched.report_routed(p_type, dest)
                        st[ptype] = False

class ControlSf(Process):
    """Control product creation"""
    def run(self, model, ordo = Schedule()):
        #initialize products struct
        create = model.modules["create"]
        obs = model.modules["obs_inSf"]
        inObs_report = obs.create_report_socket(multiple_observation = True)
        while not ordo.sf_finished():
            p_type = ordo.sf_get_next()
            yield put, self, create.request_socket, [Request("create", "create", params={'productType':p_type})]
            yield get, self, inObs_report, 1
            ordo.sf_report_done()


class ControlDispose(Process):
    def run(self, model, name):
        out = model.get_module('out'+name)
        rp_out = out.create_report_socket()
        dispose = model.get_module('dispose'+name)
        rp_dispose = dispose.create_report_socket()
        obs_out = model.get_module('obs_out'+name)
        rp_obs_out = obs_out.create_report_socket()
        while True:
            yield get, self, rp_obs_out, 1
            yield put, self, dispose.request_socket, [Request('dispose'+name, 'dispose')]


sf_process_time = [1.34, 1.06, 1.14, 1.14, 1.17, 1.13, 1.22, 1.22, 1.11, 1.23, 1.23, 1.11]
f_process_time =  [3.60, 3.49, 3.70, 3.57, 3.54, 3.75, 4.09, 3.69, 4.03, 3.62, 3.75, 3.96] 
cells = ['Sf', 'Fa', 'Fb', 'Fc']
st = dict()
inBuf = dict()
outBuf = dict()
workBuf = dict()
dispose = dict()
machine = dict()
load = dict()


def create_model():
    model = emulation.Model()
    #holders
    for i in range(1,13):
        st[i] = emulation.Holder(model, "st"+str(i))
    for i in cells:
        inBuf[i] = emulation.Holder(model, "in"+str(i))
        outBuf[i] = emulation.Holder(model, "out"+str(i))
        workBuf[i] = emulation.Holder(model, "work"+str(i))
    #actuators
    create = emulation.CreateAct(model, "create",inBuf['Sf'])
    for i in cells:
        machine[i] = emulation.ShapeAct(model, "machine"+str(i), workBuf[i])
        if i in ['Fa', 'Fb', 'Fc']:
            dispose[i] = emulation.DisposeAct(model, "dispose"+i, outBuf[i])
            machine[i]['setup'].default_time = 0
        else:
            machine[i]['setup'].default_time = 30
        load[i] = emulation.SpaceAct(model, "load"+str(i))
    transSt = emulation.SpaceAct(model, "transSt")
    transSt['setup'].default_time = 0
    #actuator's programs
    for i in cells:
        load[i].add_program('load', 0, {'source':inBuf[i], 'destination':workBuf[i]})
        load[i].add_program('unload', 0, {'source':workBuf[i], 'destination':outBuf[i]})
    for m in cells:
        if m in ['Sf']:
            process_time = sf_process_time
        else:
            process_time = f_process_time
        i = 1 
        for t in process_time:
            machine[m].add_program('p'+str(i), ("rng.normalvariate(%s, 0.5)" % t))
            i += 1
    for i in range(1,13):
        transSt.add_program('load_st'+str(i), 0, {'source':outBuf['Sf'],'destination':st[i]})
        for j in ['a', 'b', 'c']:
            transSt.add_program('unload_st'+str(i)+'to'+j, 0, {'source':st[i],'destination':inBuf['F'+j]})
    #observers
    for i in cells:
        emulation.PushObserver(model, "obs_work"+i, "work"+i+"_ready", observe_type = True, holder = workBuf[i])
        emulation.PushObserver(model, "obs_in"+i, "in"+i+"_ready", identify = True, holder = inBuf[i])
        emulation.PushObserver(model, "obs_out"+i, "out"+i+"_ready", identify = True, holder = outBuf[i])
    for i in range(1,13):
        emulation.PushObserver(model, "obs_st"+str(i),"st"+str(i)+"_ready", identify = True, holder = st[i])
    #failures (with degradation)
    #fail1 = emulation.Failure(model, "fail1", 
    #                          'rng.expovariate({0})'.format(1./100.),
    #                          'rng.expovariate({0})'.format(1./30.), 
    #                          [machine['Sf']])
    #fail1.properties['degradation'] = 0.9
    #fail1.properties['repeat'] = True
    return model
    
  
def initialize_distrib_control(model):
    
    mps = {1:1000, 2:600, 3:500, 4:2000, 5:400}
    uta = sf_process_time
    utb = f_process_time
    fin = {'a': 0, 'b': 0, 'c': 0}
    q_min = 100# bug if qmin =10 ?
    tsetup = 30
    schedule = Schedule()
    t = -50
    while sum(mps.values()) > 0:
        print "===================="
        print "date de fin", fin
        print "t=", t
        tpb = map(lambda (t, q): (t, q * utb[t]), mps.items())
        tpb.sort(key = lambda t: t[1], reverse = True)
        type_choisi = tpb[0][0]
        print "type choisi", type_choisi
        q_todo = mps[type_choisi]
        dates_fin = fin.items()
        dates_fin.sort(key = lambda t: t[1])
        (destination, date_fin) = dates_fin[0]
        
        print "duree de production", date_fin - t - tsetup
        print "qte a faire:", q_todo, "qte calculee", ceil((date_fin - t - tsetup) / uta[type_choisi])
        q = min(q_todo, max(q_min, ceil((date_fin - t - tsetup) / uta[type_choisi])))
        print "q=", q
        schedule.append_lot(type_choisi, q, destination)
        fin[destination] = t + uta[type_choisi] + q * utb[type_choisi]
        t = t + q * uta[type_choisi] + tsetup
        mps[type_choisi] = mps[type_choisi] - q 
    
    schedule.update_f_current()
    
    
    
    model.register_control(ControlDispose, 'run', (model, 'Fa'))
    model.register_control(ControlDispose, 'run', (model, 'Fb'))
    model.register_control(ControlDispose, 'run', (model, 'Fc'))
    model.register_control(CellControl, 'run', (model, 'Sf'))
    model.register_control(CellControl, 'run', (model, 'Fa'))
    model.register_control(CellControl, 'run', (model, 'Fb'))
    model.register_control(CellControl, 'run', (model, 'Fc'))
    model.register_control(ControlSt)
    model.register_control(ControlF, 'run', (model, schedule))
    model.register_control(ControlSf, 'run', (model, schedule))
    #model.register_control(DetectFailure, 'run', (model, schedule))

if __name__ == '__main__': 
    print "setting up emulation model"
    model = create_model()
    print "{0} modules in model".format(len(model.modules))
    print  "setting up control"
    initialize_distrib_control(model)
    print "{0} control classes loaded".format(len(model.control_classes))
    print "simulating..."
    model.emulate(until = 10000)
    print "simulation finished at {0}".format(model.current_time())
    chart = plot.GanttChart()
    for i in cells:
        chart.add_serie(i, machine[i])
    fig = chart.create_canvas()
    leg = chart.create_legend(columns = 1)
    #chart.save("filename.png")
    dialog = gtk.Dialog("Gantt Chart",
                        None,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
    hbox = gtk.HBox()
    hbox.pack_start(fig)
    hbox.pack_start(leg, expand = False)
    dialog.set_size_request(800, 480)
    dialog.vbox.add(hbox)
    dialog.show_all()
    dialog.connect('response', gtk.main_quit)
    dialog.connect('delete-event', gtk.main_quit)
    gtk.main()
    summary = plot.ResultSummary(model)
    print summary
    
    
    
    
