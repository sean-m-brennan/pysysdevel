"""
Factory that produces factories
"""

import sys
import functools


class FactoryException(Exception):
    def __init__(self, type_key):
        Exception.__init__(self)
        self.key = type_key

    def __str__(self):
        return "No factory for type '" + self.key + "'"


class NoDefaultFactoryException(FactoryException):
    def __init__(self, type_key):
        FactoryException.__init__(self, type_key)

    def __str__(self):
        return "No default factory for type '" + self.key + "'"


class InvalidDefinitionListException(FactoryException):
    def __init__(self, kind):
        FactoryException.__init__(self, kind)

    def __str__(self):
        return "Invalid/non-convertable definition list of type '" + \
            self.key + "'"



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

    def __str__(self):
        return str(self.module) + '.' + self.klass


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
    def __init__(self, no_default):
        list.__init__(self)
        self.no_default = no_default

    def __str__(self):
        retval = '[ '
        for d in self:
            retval += str(d) + ', '
        retval += ']'
        return retval

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
        
    @classmethod
    def from_ini(cls, list_str, no_default=False):
        lst = cls(no_default)
        # FIXME read from ini string
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
        elif type(def_list) == str:
            try:
                return DefinitionList.from_xml(def_list)
            except:
                return DefinitionList.from_ini(def_list)
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
    def __available(def_list, kwargs=None):
        d_list = DefinitionList.convert(def_list)
        if kwargs:
            return [d.name for d in d_list if d.test(**kwargs)]
        return [d.name for d in d_list]

    return functools.partial(__available, def_list)


def FactoryFactory(type_key, def_list):
    '''
    Return a factory function that creates a single requested object
    of type 'type_key' given a definition list 'def_list'.
    'def_list' must be a DefinitionList or convertable type.
    The factory creates an object corresponding to the entry
    at kwargs[type_key], or a default is there is no such entry,
    or raises an exception is there is no default.
    '''
    def __factory(type_key, def_list, kwargs):
        d_list = DefinitionList.convert(def_list)

        if not type_key in kwargs:
            if d_list.no_default:
                raise NoDefaultFactoryException(type_key)
            else:  ## first entry is default
                __import__(d_list[0].module)
                impl = sys.modules[d_list[0].module]
                constructor = getattr(impl, d_list[0].klass)
                return constructor(**kwargs)
        else:
            for d in d_list:
                if isinstance(kwargs[type_key], dict):
                    requested_class = kwargs[type_key]['type']
                else:
                    requested_class = kwargs[type_key]
                if requested_class.lower() == d.klass.lower():
                    __import__(d.module)
                    impl = sys.modules[d.module]
                    constructor = getattr(impl, d.klass)
                    return constructor(**kwargs)
        raise FactoryException(type_key)

    return functools.partial(__factory, type_key, def_list)


def ListFactoryFactory(type_key, def_list):
    '''
    Return a factory function that creates a list of requested objects
    of type 'type_key' given a definition list 'def_list'.
    'def_list' must be a DefinitionList or convertable type.
    The factory creates an object for each element of the list
    at kwargs[type_key], or a default is there is no list,
    or raises an exception is there is no default.
    '''
    def __listfactory(type_key, def_list, kwargs):
        d_list = DefinitionList.convert(def_list)

        obj_list = []
        if not type_key in kwargs:
            if d_list.no_default:
                raise NoDefaultFactoryException(type_key)
            else:  ## first entry is default
                __import__(d_list[0].module)
                impl = sys.modules[d_list[0].module]
                constructor = getattr(impl, d_list[0].klass)
                return [constructor(**kwargs)]
        else:
            for requested_class in kwargs[type_key]:
                if isinstance(requested_class, dict):
                    requested_class = requested_class['type']
                for d in d_list:
                    if requested_class.lower() == d.klass.lower():
                        __import__(d.module)
                        impl = sys.modules[d.module]
                        constructor = getattr(impl, d.klass)
                        obj_list.append(constructor(**kwargs))
                        break
            return obj_list
        raise FactoryException(type_key)

    return functools.partial(__listfactory, type_key, def_list)
