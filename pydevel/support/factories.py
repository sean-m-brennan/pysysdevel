# Factory that produces factories
#**************************************************************************
# 
# This material was prepared by the Los Alamos National Security, LLC 
# (LANS), under Contract DE-AC52-06NA25396 with the U.S. Department of 
# Energy (DOE). All rights in the material are reserved by DOE on behalf 
# of the Government and LANS pursuant to the contract. You are authorized 
# to use the material for Government purposes but it is not to be released 
# or distributed to the public. NEITHER THE UNITED STATES NOR THE UNITED 
# STATES DEPARTMENT OF ENERGY, NOR LOS ALAMOS NATIONAL SECURITY, LLC, NOR 
# ANY OF THEIR EMPLOYEES, MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR 
# ASSUMES ANY LEGAL LIABILITY OR RESPONSIBILITY FOR THE ACCURACY, 
# COMPLETENESS, OR USEFULNESS OF ANY INFORMATION, APPARATUS, PRODUCT, OR 
# PROCESS DISCLOSED, OR REPRESENTS THAT ITS USE WOULD NOT INFRINGE 
# PRIVATELY OWNED RIGHTS.
# 
#**************************************************************************


class NoDefaultFactoryException(Exception):
    def __init__(self, type_key):
        Exception.__init__(self)
        self.key = type_key

    def __str__(self):
        return 'No default factory for type ' + self.key


class InvalidDefinitionListException(Exception):
    def __init__(self, kind):
        Exception.__init__(self)
        self.kind = kind

    def __str__(self):
        return 'Invalid/non-convertable definition list of type ' + self.kind



class Definition(object):
    '''
    Definition for use in factory constructors. Takes a display name
    (which must be identical to the class name exclusing whitespace),
    a module name, and an optional test function.
    '''
    def __init__(self, name, mod, test=lambda(x): True):
        self.name = name
        self.klass = ''.join(name.split())
        self.module = mod
        self.test = test


class DefinitionList(list):
    '''
    A list of Definitions. Allows for conversion.
    XML must be in the form:
    <definitions>
      <definition test="lambda(x): x == 1">
        <name>Example</name>
        <module>ex</module>
      </definition>
    </definitions>
    '''
    def __init__(self):
        list.__init__(self)
        self.no_default = False

    @classmethod
    def from_list(cls, tpl_list, no_default=False):
        lst = cls(no_default)
        for t in tpl_list:
            lst.append(Definition(*t))
        return lst

    @classmethod
    def from_xml(cls, list_str, no_default=False):
        import xml.etree.ElementTree as ET
        lst = cls(no_default)
        definitions = ET.fromstring(list_str)
        for d in definitions.findAll('definition'):
            if 'test' in d.attrib:
                test = d['test']
            else:
                test = 'lambda(x): True'
            lst.append(Definition(d.find('name').text, d.find('module'.text),
                                  eval(test)))
        return lst
        
    @staticmethod
    def convert(def_list):
        '''
        Convert from either a tuple list or a string descriptor
        to DefinitionList.
        Conversion always uses the first entry as the default.
        '''
        if type(def_list) == list:
            return DefinitionList.from_list(def_list)
        elif type(def_list) == list:
            return DefinitionList.from_xml(def_list)
        elif type(def_list) == type(DefinitionList):
            return def_list
        else:
            raise InvalidDefinitionListException(type(def_list))



def AvailableFactory(def_list):
    '''
    Returns a function that lists available definitions.
    Usually assigned to a name as 'get_available_' + type_key,
    as in 'get_available_plots = AvailableFactory(plots)'.
    '''
    def __available(kwargs):
        def_list = DefinitionList.convert(def_list)
        return [d.name for d in def_list if d.test(**kwargs)]

    return __available


def FactoryFactory(type_key, def_list):
    '''
    Return a factory function that creates a single requested object
    of type 'type_key' given a definition list 'def_list'.
    'def_list' must be a DefinitionList or convertable type.
    The factory creates an object corresponding to the entry
    at kwargs[type_key], or a default is there is no such entry,
    or raises an exception is there is no default.
    '''
    def __factory(kwargs):
        def_list = DefinitionList.convert(def_list)

        if not type_key in kwargs:
            if def_list.no_default:
                raise NoDefaultFactoryException(type_key)
            else:  ## first entry is default
                __import__(def_list[0].module)
                impl = sys.modules[def_list[0].module]
                constructor = getattr(impl, def_list[0].klass)
                return constructor(**kwargs)
        else:
            for def in def_list:
                if kwargs[type_key] == def.klass:
                    __import__(def.module)
                    impl = sys.modules[def.module]
                    constructor = getattr(impl, def.klass)
                    return constructor(**kwargs)

    return __factory


def ListFactoryFactory(type_key, def_list):
    '''
    Return a factory function that creates a list of requested objects
    of type 'type_key' given a definition list 'def_list'.
    'def_list' must be a DefinitionList or convertable type.
    The factory creates an object for each element of the list
    at kwargs[type_key], or a default is there is no list,
    or raises an exception is there is no default.
    '''
    def __listfactory(kwargs):
        def_list = DefinitionList.convert(def_list)

        obj_list = []
        if not type_key in kwargs:
            if def_list.no_default:
                raise NoDefaultFactoryException(type_key)
            else:  ## first entry is default
                __import__(def_list[0].module)
                impl = sys.modules[def_list[0].module]
                constructor = getattr(impl, def_list[0].klass)
                return [constructor(**kwargs)]
        else:
            for klass in kwargs[type_key]:
                for def in def_list:
                    if klass == def.klass:
                        __import__(def.module)
                        impl = sys.modules[def.module]
                        constructor = getattr(impl, def.klass)
                        obj_list.append(constructor(**kwargs))
                        break
            return obj_list

    return __listfactory
