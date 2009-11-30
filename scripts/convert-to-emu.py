
import sys, logging, zipfile
sys.path.insert(0, '../src')
logger = logging.getLogger('convert_to_new_xml')

from emulica.emuML import EmulationWriter, EmuFile
from emulica import emulation, properties


class OldEmulationParser:
    """This class can be used to get an Emulation Model from an xml file."""
    def __init__(self, string, model = None, parent = None, name = 'main', path = None):
        """Create a new instance of a emulicaML.EmulationParser. When the object is 
        created, the string is parsed, and submodels list is built. Beware: the
        submodels files are opened at this stage ! If the model argument is 
        specified, it is used to laod modules into, else a new model is created 
        using the kwargs.
        
        Arguments:
            string -- the model into which load modules or from which extract modules
            model -- the model to load modules into
            *kwargs -- keywords argumenst to be passed to the Model constructor
        Raises:
            ???Error -- if string is not well formed   
         
        """
        from xml.etree.ElementTree import fromstring
        self.tree = fromstring(string)
        self.unmarshall_mapping = {'program_table': self.__parse_prog,
                                   'setup': self.__parse_setup}
        self.model = model or emulation.Model(model = parent, name = name, path = path)
        self.submodels = dict()
        mod_root = self.tree.find("modules")
        for submodel_elt in mod_root.findall("submodel"):
            #try loading gseme file for every submodels
            sub_path = submodel_elt.get('path')
            sub_path = sub_path[0:-5]+'emu'
            sub_name = submodel_elt.get('name')
            gsf = EmuFile(sub_path, 'r', parent_model = self.model, name = sub_name)
            #TODO: if opening fails, add name to a list of broken submodels
            self.submodels[sub_name] = gsf
        self.renaming = dict()
    
    def load_submodels(self):
        """Load submodels in the model"""
        for (name, gsf) in self.submodels.items():
            (submodel, subcontrol) = gsf.read()
            #compile and register control in model
            #compile_control(submodel, subcontrol)    
    
    
    def parse(self):
        """Load a set of modules from an XML string or treeset into the model, 
        and Return the list of created modules.
        
        Arguments:
            string -- an XML string that represent the model.
            
        Return 
            the list of created modules
        
        """
        
        mod_root = self.tree.find("modules")
        mod_list = []
        attributes = dict()
        #loads submodels first (if any)
        self.load_submodels()
        #loads modules
        for mod_elt in mod_root.findall("module"):
            mod_type = mod_elt.get("type")
            name = mod_elt.get("name")
            if name in self.model.modules:
                new_name = mod_type+str(len(self.model.modules))
                self.renaming[name] = new_name
                name = new_name
            logger.info("creating module: " + name + " of type: "+mod_type)
            mod_class = getattr(emulation, mod_type)
            mod = mod_class(self.model, name)
            mod_list.append(mod)
            attributes[mod] = mod_elt.findall("attribute")
            
        #build model structure
        for mod, attribute_list in attributes.items():
            for elt in attribute_list:
                name = elt.get("name")
                logger.info("processing attribute: "+ name)
                if name in self.unmarshall_mapping.keys():
                    parse_fn = self.unmarshall_mapping[name]
                else:
                    parse_fn = self.__parse
                value = parse_fn(mod, elt)
                mod.properties[name] = value
         
        #get inputs
        interface_root = self.tree.find("interface")
        if not interface_root is None:
            for input_elt in interface_root.findall("input"):
                name = input_elt.get("name")
                module = input_elt.get("module")
                prop = input_elt.get("property")
                self.model.inputs[name] = (module, prop)
            #if model has parent, call apply_inputs
            if not self.model.is_main:
                self.model.apply_inputs()
        return mod_list

    def __parse(self, module, element):
        """Parse a module attribute and return the resulting object
        
        Arguments:
            element -- the Element to parse
        
        Returns:
            the parsed value
            
        """
        if "reference" in element.keys():
            name = element.get("reference")
            if name in self.renaming:
                name = self.renaming[name]
            return self.model.get_module(name)
        elif "value" in element.keys():
            try:
                return eval(element.get("value"))
            except (NameError, AttributeError):
                return element.get("value")
        else:
            if 'type' in element.keys():
                t = getattr(__builtins__, element.attrib['type'])
                r = t()
            else:
                r = None
            for elt in element.findall('element'):
                if 'name' in elt.keys():
                    if r == None:
                        r = dict()
                    r[elt.attrib['name']] = self.__parse(module, elt)
                else:
                    if r == None:
                        r = list()
                    r.append(self.__parse(module, elt))
            return r
        
    def __parse_prog(self, module, element):
        """Parse a program table and return the resulting object.

        Arguments:
            element -- the Element to parse

        Returns:
            the parsed program table (type dictionary)
            
        """
        table = dict()
        for program in element.findall('program'):
            delay = program.get("delay")
            #get transform
            #TODO: 
            p = properties.Program(module.properties, delay)
            for elt in program.findall('element'):
                p.transform[elt.get("name")] = self.__parse(module, elt)
            
            name = program.get("name")
            table[name] = p
        return table

    def __parse_setup(self, module, element):
        """Parse a setup table and return the resulting object.
        
        Arguments:
            element -- the Element to parse
        
        Returns:
            the parsed program table (type dictionary)
       
        """
        default_delay = eval(element.get("default_delay"))
        setup = properties.SetupMatrix(module.properties, default_delay)
        for s in element.findall('setup'):
            delay = eval(s.get("delay"))
            init = s.get("initial")
            final = s.get("final")
            setup.add(init, final, delay)
        return setup
        
        
def convert_xml(source):
    """Convert the XML string source (in the old format) to the new format."""
    model = emulation.Model()
    
    old_parser = OldEmulationParser(source_str, model)
    old_parser.parse()
    for module in model.modules.values():
        if module.__class__.__name__ == 'CreateAct':
            old_dict = module.properties['product_prop']
            module.properties['product_prop'] = properties.ChangeTable(module.properties, 'product_prop')
            for (k, v) in old_dict.items():
                module.properties['product_prop'][k] = v    
        if module.__class__.__name__ in ['ShapeAct', 'SpaceAct', 'AssembleAct', 'DisassembleAct']:
            old_dict = module.properties['program_table']
            module.properties['program_table'] = properties.ProgramTable(module.properties,
                                                                         'program_table', 
                                                                         module.program_keyword)
            for (k, v) in old_dict.items():
                #print k, v
                for (transf_name, transf_value) in v.transform.items():
                    if transf_name == 'change':
                        old_dict2 = transf_value or {}
                        v.transform[transf_name] = properties.ChangeTable(module.properties, 'program_table')
                        for (chg_name, chg_v) in old_dict2.items():
                            v.transform[transf_name][chg_name] = chg_v    
                module.properties['program_table'].add_program(k, v.time_law, v.transform)
            #print module.properties['program_table']
    new_writer = EmulationWriter(model)
    new_str = new_writer.write()
    return new_str
    
    
    
if __name__ == '__main__':
    source_path = sys.argv[1]
    
    if source_path.endswith('.gseme'):
        #open zipfile and get XML
        zfile = zipfile.ZipFile(source_path, 'r')
            
        namelist = zfile.namelist()
        if 'emulation.xml' in namelist:
            source_str = zfile.read('emulation.xml')
            result = convert_xml(source_str)
            control = zfile.read('control.py')
            props = zfile.read('props.db')
            zfile.close()
            dest_path = source_path[0:-5]+'emu'    
            destfile = zipfile.ZipFile(dest_path, 'w')
            
            destfile.writestr('emulation.xml', result)
            destfile.writestr('props.db', props)
            destfile.writestr('control.py', control)
            
            destfile.close()
        else:
            print "wrong format: emulation.xm not found"
        
    else:
        source_str = source.read()
        result = convert_xml(open(source_str, 'r'))
        print result
   
