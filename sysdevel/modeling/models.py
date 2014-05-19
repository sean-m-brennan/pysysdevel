"""
Copyright 2013.  Los Alamos National Security, LLC.
This material was produced under U.S. Government contract
DE-AC52-06NA25396 for Los Alamos National Laboratory (LANL), which is
operated by Los Alamos National Security, LLC for the U.S. Department
of Energy. The U.S. Government has rights to use, reproduce, and
distribute this software.  NEITHER THE GOVERNMENT NOR LOS ALAMOS
NATIONAL SECURITY, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
modified to produce derivative works, such modified software should be
clearly marked, so as not to confuse it with the version available
from LANL.

Licensed under the Mozilla Public License, Version 2.0 (the
"License"); you may not use this file except in compliance with the
License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/2.0/

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing
permissions and limitations under the License.
"""
# pylint: disable=W0105
"""
Model-View-Controller base classes
"""

import os
import shutil
import math
from itertools import combinations
try:
    import json
except ImportError:
    import simplejson as json

from .websockethandler import json_handler

class UnknownModelException(Exception):
    def __init__(self, explain):
        Exception.__init__(self)
        self.what = explain

    def __str__(self):
        return 'Unknown model ' + self.what


class UnmatchedModelException(Exception):
    def __init__(self, explain):
        Exception.__init__(self)
        self.what = explain

    def __str__(self):
        return 'Unmatched model ' + self.what



##############################

class DataModel(dict):
    '''
    Model of Model-View-Controller pattern. Container for data updates by
    multiple controllers, read by viewer for display.
    '''

    DATE_FORMAT = '%Y-%m-%d'
    TIME_FORMAT = '%H:%M:%S'
    DATETIME_SEP = 'T'
    DATETIME_TZ = 'Z'
    DATETIME_FORMAT = DATE_FORMAT + DATETIME_SEP + TIME_FORMAT + DATETIME_TZ

    def __init__(self, template=()):
        dict.__init__(self)
        self._pipeline = dict()
        self._index = 0
        try:
            d = dict(template)
        except ValueError:
            d = dict([(k, None) for k in template])
        for k, v in d.items():
            self[k] = v


    def __getattr__(self, attr):
        return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value


    def add_step(self, controller):
        '''
        Add a producer/consumer to the pipeline.
        '''
        self._pipeline[self._index] = controller
        self._index += 1


    def validate(self):
        '''
        Check if the producer/consumer pipeline operating on this data model
        fulfills the requirements at each step.
        '''
        prev = None
        for idx in range(len(self._pipeline)):
            ctrlr = self._pipeline[idx]
            if prev:
                reqs = list(ctrlr.requires())
                for p in prev.provides():
                    reqs.remove(p)
                if len(reqs) > 0:
                    return False
            prev = ctrlr
        return True


    @classmethod
    def satisfies(cls, parameters, obj):
        '''
        Tests if values satisfy parameters.
        obj is dictionary-like
        '''
        tests = [True] * len(parameters)
        for i, (k, v) in enumerate(parameters.items()):
            data = obj[k]
            try:
                r = sorted(v)
                if data < r[0] or data > r[-1]:
                    tests[i] = False
            except TypeError:
                if data != v:
                    tests[i] = False
        return sum(tests)



class CSVDataModel(DataModel):
    '''
    Comma-separated-value storage-backed data. Represents one row of a file.
    '''
    FIELD_SEP = ','

    def __init__(self, template=()):
        super(CSVDataModel, self).__init__(template)


    def header(self):
        return self.FIELD_SEP.join(self.keys())


    def fromstr(self, line, parameters=()):
        params = dict(parameters)
        if self.satisfies(params, (self.keys(), line)):
            for i, k in enumerate(self.keys()):
                self[k] = line.split(self.FIELD_SEP)[i]
        else:
            raise UnmatchedModelException('Parameters not satified: ' +
                                          str(params))


    def __str__(self):
        return self.FIELD_SEP.join(self.values()) + '\n'


    @classmethod
    def satisfies(cls, parameters, obj):
        keys, line = obj
        indices = dict([(k, i) for i, k in enumerate(keys)])
        tests = [True] * len(parameters)
        for i, (k, v) in enumerate(parameters.items()):
            data = line.split(cls.FIELD_SEP)[indices[k]]
            try:
                r = sorted(v)
                if data < r[0] or data > r[-1]:
                    tests[i] = False
            except TypeError:
                if data != v:
                    tests[i] = False
        return sum(tests)



class JSONDataModel(DataModel):
    '''
    JSON-encoded storage-backed data. Represents one row of a file.
    '''
    FIELD_SEP = ' | '

    def __init__(self, template=()):
        super(JSONDataModel, self).__init__(template)


    def header(self):
        return self.FIELD_SEP.join(self.keys())


    def fromstr(self, line, parameters=()):
        params = dict(parameters)
        if self.satisfies(params, (self.keys(), line)):
            for i, k in enumerate(self.keys()):
                self[k] = json.loads(line.split(self.FIELD_SEP)[i])
        else:
            raise UnmatchedModelException('Parameters not satified: ' +
                                          str(params))


    def __str__(self):
        row = [json.dumps(self[k], default=json_handler) for k in self.keys()]
        return self.FIELD_SEP.join(row) + '\n'


    @classmethod
    def satisfies(cls, parameters, obj):
        keys, line = obj
        indices = dict([(k, i) for i, k in enumerate(keys)])
        tests = [False] * len(parameters)
        for i, (k, v) in enumerate(parameters.items()):
            data = line.split(cls.FIELD_SEP)[indices[k]]
            try:
                r = sorted(v)
                if data < r[0] or data > r[-1]:
                    tests[i] = False
            except TypeError:
                if data != v:
                    tests[i] = False
        return sum(tests)



####################

class DataStore(object):
    '''
    Storage-backed data-model collection.

    Extend for non-text files.
    '''
    def __init__(self, klass, name, directory, keys, ext='dat'):
        self.klass = klass
        self.name = name
        self.path = os.path.join(directory, name + '.' + ext)
        self.fields = keys
        self.data_models = {}  # dict of (line-number, data-model-idx) tuples
        self.last_idx = 0


    def check_validity(self):
        '''
        Test if file contents correspond to the expected data structure.
        '''
        if not os.path.exists(self.path):
            raise UnmatchedModelException(os.path.basename(self.path) +
                                          ' does not exist.')
        data_file = open(self.path, mode='r')
        line = data_file.readline()
        data_file.close()
        if line == self.klass.header():
            raise UnmatchedModelException(os.path.basename(self.path) +
                                          ' is not a ' + self.klass.__name__ +
                                          ' data model store.')

    def check_consistency(self, data_models):
        how_many = 0
        for d1, d2 in combinations(data_models):
            if not d1.header() == d2.header():
                how_many += 1
        if how_many:
            raise UnmatchedModelException('Inconsistent data collection: ' +
                                          str(how_many) +
                                          ' do not match model signature.')
        return self.klass.FIELD_SEP.join(self.fields)


    def add(self, obj):
        '''
        Add-in an additional data-model.
        '''
        if isinstance(obj, dict):
            template = dict(obj)
            obj = self.klass(template)
        if not isinstance(obj, self.klass) or obj.keys() != self.fields:
            raise UnmatchedModelException('Attempting to add unmatched ' +
                                          'data model to collection.')
        self.last_idx += 1
        self.data_models[self.last_idx] = obj


    def load(self, parameters=()):
        '''
        Populate the data objects from file.
        '''
        params = dict(parameters)
        self.check_validity()
        data_file = open(self.path, mode='r')
        for idx, line in enumerate(data_file):
            try:
                obj = self.klass(self.fields)
                obj.fromstr(line, params)
                self.data_models[idx] = obj
                self.last_idx = idx
            except UnmatchedModelException:
                pass
        data_file.close()


    def unload(self):
        '''
        Store the data objects to file.
        '''
        header = self.check_consistency(self.data_models.values())
        written = []
        out_exists = os.path.exists(self.path)
        if out_exists:
            self.check_validity()
            shutil.move(self.path, self.path + '.tmp')
            data_in_file = open(self.path + '.tmp', 'r')
        data_out_file = open(self.path, mode='a')
        data_out_file.write(header + '\n')
        if out_exists:
            for idx, line in enumerate(data_in_file):
                try:
                    ## changed lines
                    data_out_file.write(str(self.data_models[idx]) + '\n')
                    written.append(idx)
                except KeyError:
                    ## lines not changed/ingested
                    data_out_file.write(line + '\n')
        for idx, data in self.data_models.items():
            if not idx in written:
                ## data that is new
                data_out_file.write(str(data) + '\n')
        if out_exists:
            data_in_file.close()
            os.remove(self.path + '.tmp')
        data_out_file.close()



try:
    import h5py
    import numpy

    class HDF5DataModel(DataModel):
        '''
        HDF5 storage-backed data. Represents one row of a file.
        '''
        def __init__(self, template=()):
            '''
            Template can be a dictionary of dictionaries for implementing
            multilevel attributes.
            Basic type is an array.
            '''
            super(HDF5DataModel, self).__init__(template)


        @classmethod
        def satisfies(cls, parameters, obj):
            tests = [True] * len(parameters)
            for i, (k, v) in enumerate(parameters.items()):
                for data in obj[k]:
                    try:
                        r = sorted(v)
                        if data < r[0] or data > r[-1]:
                            tests[i] = False
                    except TypeError:
                        if data != v:
                            tests[i] = False
            return sum(tests)



    class HDF5DataStore(DataStore):
        '''
        HDF5 storage-backed data container.
        Represents one specific group in the hierarchy of the file.
        Description is a nested dictionary where leaves are types.
        '''
        def __init__(self, name, directory, description,
                     hierarchy=(), dm=HDF5DataModel):
            super(HDF5DataStore, self).__init__(dm, name, directory,
                                            description, 'h5')
            self.hierarchy = list(hierarchy)
            self.data_models = []


        def __recur(self, head, items, do_this, assign=False):
            for k, v in items:
                try:
                    if isinstance(v, dict):
                        self.__recur(head[k], v.items(), do_this, assign)
                    elif assign:
                        head[k] = do_this(head[k])
                    else:
                        do_this(head[k])
                except KeyError:
                    filename = os.path.basename(self.path)
                    raise UnmatchedModelException(filename + ' is not a ' +
                                                  self.klass.__name__ +
                                                  ' data model store.')


        def check_validity(self):
            if not os.path.exists(self.path):
                raise UnmatchedModelException(os.path.basename(self.path) +
                                              ' does not exist.')
            h5file = open(self.path, mode='r')
            self.__recur(h5file, self.fields.items(), lambda: None)
            h5file.close()


        def add(self, obj):
            '''
            Add-in an additional data-model.
            '''
            if isinstance(obj, dict):
                template = dict(obj)
                self.__recur(template, template.items(),
                             lambda x: None if isinstance(x, type) else x, True)
                obj = self.klass(template)
            if not isinstance(obj, self.klass) or obj.keys() != self.fields:
                raise UnmatchedModelException('Attempting to add unmatched ' +
                                              'data model to collection.')
            self.data_models.append(obj)


        def load(self, parameters=()):
            params = dict(parameters)
            self.check_validity()
            h5file = h5py.File(self.path, mode='r')
            node = h5file
            for path in self.hierarchy:
                for level in path.split('/'):
                    if level:
                        node = node[level]
                for data in node:
                    if self.klass.satisfies(params, data):
                        template = dict(self.fields)
                        ## set all leaves to None
                        self.__recur(template, template.items(),
                                     lambda: None, True)
                        obj = self.klass(template)
                        for k in obj.keys():
                            obj[k] = numpy.array(data[k]) ##FIXME field type?
                            #FIXME shape??
                        self.data_models.append(obj)
            h5file.close()


        def unload(self):
            h5file = h5py.File(self.path, mode='w')
            node = h5file
            for path in self.hierarchy:
                for level in path.split('/'):
                    if level:
                        node = node[level]
                for data in self.data_models:
                    for k, v in data:
                        node[k] = v
            h5file.close()


    

    try:
        from spacepy import datamodel

        class SpaceDataModel(datamodel.SpaceData):
            '''
            HDF5 storage-backed spacepy datamodel. Represents one row of a file.
            '''
            @classmethod
            def satisfies(cls, parameters, obj):
                tests = [True] * len(parameters)
                for i, (k, v) in enumerate(parameters.items()):
                    for data in obj[k]:
                        try:
                            r = sorted(v)
                            if data < r[0] or data > r[-1]:
                                tests[i] = False
                        except TypeError:
                            if data != v:
                                tests[i] = False
                return sum(tests)



        class SpaceDataStore(HDF5DataStore):
            def __init__(self, name, directory, description,
                         hierarchy=(), dm=SpaceDataModel):
                super(SpaceDataStore, self).__init__(name, directory,
                                                     description, hierarchy, dm)


            ##FIXME


    except ImportError:
        pass

except ImportError:
    pass


##############################

class DataController(object):
    '''
    Controller of Model-View-Controller pattern. Manipulates the attributes
    of a model to reflect computation.
    '''

    def _js_provides(self):
        discard = dir(type('dummy', (object,), {}))  ## builtins
        discard += [item for item in dir(self) if callable(item)]  ## methods
        return [item for item in dir(self) if item not in discard]

    def _py_provides(self):
        ##  The following is not supported under PyJS
        import inspect
        discard = dir(type('dummy', (object,), {}))
        discard += inspect.getmembers(self,
                                      lambda x: inspect.isbuiltin(x) or \
                                      inspect.ismethod(x))
        return [item for item in inspect.getmembers(self)
                if item not in discard]

    def provides(self):
        '''
        Outputs; relevant attributes and properties.
        '''
        ## Test whether inside pyjamas
        try:
            import pyjd  # pylint: disable=F0401
            if not pyjd.is_desktop:
                return self._js_provides()
            else:
                return self._py_provides()
        except ImportError:
            return self._py_provides()

    def requires(self):
        '''
        Necessary inputs; may be an empty list (for data acquisition objects).
        '''
        return []

    def control(self, data_model):
        '''
        Exerts control on the given data model, using the data_model attributes
        listed by 'requires()' and adding attributes listed by 'provides()'
        to the data_model object.
        '''
        raise NotImplementedError()



##############################

class DataViewer(object):
    '''
    View of Model-View-Controller pattern. Passively reads model attributes
    to produce a display.
    '''

    def requires(self):
        '''
        Necessary inputs.
        '''
        raise NotImplementedError()


    def view(self, data_model):
        '''
        Using the data_model attributes listed by 'requires()'
        '''
        raise NotImplementedError()




class GenericPlot(DataViewer):
    '''
    General graphing viewer, may display several PlotSeries.
    Usage::

        for datum in data:
            plot.view(datum)
        plot.plot()

    '''
    ## Also an abstract class  # pylint: disable=W0223
    def __init__(self, axes=2):
        DataViewer.__init__(self)
        self.chart_title = 'Chart'
        self.axes = axes
        self._series = []


    @property
    def series(self):
        d = dict()
        for s in self._series:
            for z in dir(s):
                d[z] = getattr(s, z)
        return d


    def requires(self):
        return []


    def add(self, series):
        self._series.append(series)


    def __dir__(self):
        return ['chart_title', 'series']


    def view(self, data_model_list):
        '''
        Must override this method since 'view' is not
        implemented for PlotSeries.
        '''
        s = PlotSeries(self.axes)
        s.view(data_model_list)
        self._series.append(s)


    def plot(self):
        import pylab as plot

        fig = plot.figure()
        for s in self._series:
            axes = fig.add_subplot(111)
            if s.axes == 3:
                axes.plot(s.x_values, s.y_values, s.z_values)
                axes.xlabel(s.labels[0])
                axes.ylabel(s.labels[1])
                axes.zlabel(s.labels[2])
            else:
                axes.plot(s.x_values, s.y_values)
                axes.xlabel(s.labels[0])
                axes.ylabel(s.labels[1])
            axes.title(s.series_name)
        plot.show()



class PlotSeries(DataViewer):
    '''
    Abstract plotting class, represents a single two or three axis data series.
    '''
    def __init__(self, *args, **kwargs):  # pylint: disable=W0613
        self.name = 'Series'
        self.axes = kwargs.get('axes', 2)
        self.x_values = []
        self.y_values = []
        self.z_values = []
        self.labels = ['', '', '']


    def view(self, data_model):
        '''
        Given a DataModel, compute the plot values.
        '''
        raise NotImplementedError()


    def __dir__(self):
        if self.axes == 3:
            return ['name', 'labels', 'x_values', 'x_ticks',
                    'y_values', 'y_ticks', 'z_values', 'z_ticks']
        else:
            return ['name', 'labels', 'x_values', 'x_ticks',
                    'y_values', 'y_ticks']

    @property
    def x_ticks(self):
        if len(self.x_values) < 1:
            return [-1, 1]
        lo = int(min(self.x_values))-1
        hi = int(max(self.x_values))+2
        if hi - lo < 10:
            step = 1
        else:
            step = (hi - lo) / 10
        try:
            return list(range(lo, hi, step))
        except ValueError:
            return list(range(lo, hi))

    @property
    def y_ticks(self):
        if len(self.y_values) < 1:
            return [-1, 1]
        mx = abs(max(self.y_values) - min(self.y_values))
        if mx < 10:
            degree = 2
        else:
            degree = (10 ** int(math.log10(mx))) / 2
        lo = int(min(self.y_values))-1
        hi = int(max(self.y_values))+degree
        if hi - lo < 10:
            step = 1
        else:
            step = (hi - lo) / 10
        try:
            return list(range(lo, hi, step))
        except ValueError:
            return list(range(lo, hi))

    @property
    def z_ticks(self):
        if len(self.z_values) < 1:
            return [-1, 1]
        if len(self.z_values) < 2:
            return [int(self.z_values[0] - 1), int(self.z_values[0] + 1)]
        lo = int(min(self.z_values))-1
        hi = int(max(self.z_values))+1
        if hi - lo < 10:
            step = 1
        else:
            step = (hi - lo) / 10
        try:
            return list(range(lo, hi, step))
        except ValueError:
            return list(range(lo, hi))
