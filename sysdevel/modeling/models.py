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

import math
import numpy
from datetime import datetime
try:
    import json
except ImportError:
    import simplejson as json


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

try:
    from spacepy import datamodel as spdm
    dm_klass = spdm.SpaceData
    USE_SPACEPY = True
except ImportError:
    dm_klass = dict
    USE_SPACEPY = False


def json_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, numpy.ndarray):
        return obj.tolist()
    elif USE_SPACEPY and isinstance(obj, spdm.dmarray):
        return obj.tolist()
    elif USE_SPACEPY and isinstance(obj, spdm.SpaceData):
        keyed_values = [str(k) + ':' + json.dumps(v, default=json_handler)
                        for k, v in obj.items()]
        attributes = json.dumps(obj.attrs, default=json_handler)
        if attributes:
            keyed_values.append('ATTRS:' + attributes) 
        return '{' + ','.join(keyed_values) + '}'
    elif isinstance(obj, DataViewer):
        import inspect
        discard = dir(type('dummy', (object,), {}))
        inspector = lambda x: inspect.isbuiltin(x) or inspect.ismethod(x)
        discard += inspect.getmembers(obj, inspector)
        return [item for item in inspect.getmembers(obj) if item not in discard]
    else:
        raise TypeError('Object of type ' + type(obj) + ' with value of ' +
                        repr(obj) + ' is not JSON serializable.')


def json_spacedata_decoder(obj):
    '''
    Recursive decoding of JSON-encoded SpaceData object
    '''
    if USE_SPACEPY and isinstance(obj, dict) and 'ATTRS' in obj.keys():
        data_model = spdm.SpaceData()
        for k, v in obj:
            if k.upper() == 'ATTRS':
                data_model.attrs = v
            else:
                data_model[k] = json_spacedata_decoder(v)
        return data_model
    else:
        return obj



class DataModel(dm_klass):
    '''
    Model of Model-View-Controller pattern. Container for data, updated by
    multiple controllers, read by viewer for display.

    Represents keyed access to data arrays.

    If SpacePy is available, this object can also have attributes.
    Also, CDF file backing is only supported through SpacePy.
    '''

    DATE_FORMAT = '%Y-%m-%d'
    TIME_FORMAT = '%H:%M:%S'
    DATETIME_SEP = 'T'
    DATETIME_TZ = 'Z'
    DATETIME_FORMAT = DATE_FORMAT + DATETIME_SEP + TIME_FORMAT + DATETIME_TZ

    def __init__(self, *args, **kwargs):
        '''
        Other than superclass (dict) keyword arguments,
        this can take a 'template' keyword
        which is either a dictionary for populating keys and values
        or a list of keys.

        If SpacePy is available, this can also take a 'attrs' keyword for 
        populating the attributes dictionary.
        '''
        template = ()
        if 'template' in kwargs:
            template = kwargs['template']
            del kwargs['template']
        super(DataModel, self).__init__(*args, **kwargs)
        self._pipeline = list()
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
        self._pipeline.append(controller)


    def validate(self):
        '''
        Check if the producer/consumer pipeline operating on this data model
        fulfills the requirements at each step.
        '''
        prev = None
        for controller in self._pipeline:
            if prev:
                reqs = list(controller.requires())
                for p in prev.provides():
                    reqs.remove(p)
                if len(reqs) > 0:
                    return False
            prev = controller
        return True


    def satisfies(self, parameters):
        '''
        Tests whether the dataset satisfies keyed parameters.
        A range can be specified with a list.
        '''
        passes = True
        for k, v in parameters.items():
            if USE_SPACEPY and k.upper() == 'ATTRS':
                for ak, av in v.items():
                    attr = self.attrs[ak]
                    try:
                        arng = sorted(av)
                        if attr < arng[0] or attr > arng[-1]:
                            passes = False
                    except TypeError:
                        if attr != av:
                            passes = False
                continue
            try:
                data_array = self[k]
            except KeyError:
                passes = False
                continue
            try:
                len(data_array)
            except TypeError:
                data_array = [data_array]
            for datum in data_array:
                try:
                    rng = sorted(v)
                    if datum < rng[0] or datum > rng[-1]:
                        passes = False
                except TypeError:
                    if datum != v:
                        passes = False
        return passes


    @classmethod
    def fromSpaceData(cls, sd, data_model=None):
        '''
        Convert a SpaceData object to a DataModel object.
        If 'data_model' is None, return a new DataModel object,
        otherwise, modify 'data_model'.
        '''
        if data_model is None:
            kwargs = {}
            try:
                kwargs['attrs'] = sd.attrs
            except AttributeError:
                pass
            return cls(template=dict(sd), **kwargs)  # pylint: disable=W0142
        else:
            try:
                data_model.attrs = sd.attrs
            except AttributeError:
                pass
            for k, v in sd.items():
                data_model[k] = v


    @classmethod
    def fromCDF(cls, filepath, **kwargs):
        '''
        Create a DataModel from a CDF data file.
        Not available without SpacePy.
        '''
        if USE_SPACEPY:
            return cls.fromSpaceData(spdm.fromCDF(filepath, **kwargs))
        else:
            raise NotImplementedError


    def toCDF(self, filepath, **kwargs):
        '''
        Save this DataModel to a CDF data file.
        Not available without SpacePy.
        '''
        if USE_SPACEPY:
            spdm.toCDF(filepath, self, **kwargs)
        else:
            raise NotImplementedError
        

    @classmethod
    def fromHDF5(cls, filepath, **kwargs):
        '''
        Create a DataModel from a HDF5 data file.
        Attributes are not available without SpacePy.
        '''
        if USE_SPACEPY:
            return cls.fromSpaceData(spdm.fromHDF5(filepath, **kwargs))
        else:
            import h5py
            data_model = cls()
            path = '/'
            if 'path' in kwargs:
                path = kwargs['path']
            h5file = h5py.File(filepath, mode='r')
            for key in h5file[path]:
                data_model[key] = numpy.array(h5file[path][key])
            h5file.close()
            return data_model


    def toHDF5(self, filepath, **kwargs):
        '''
        Save this DataModel to a HDF5 data file.
        Attributes are not available without SpacePy.
        '''
        if USE_SPACEPY:
            spdm.toHDF5(filepath, self, **kwargs)
        else:
            import h5py
            path = '/'
            if 'path' in kwargs:
                path = kwargs['path']
            h5file = h5py.File(filepath, mode='w')
            for k, v in self.items():
                h5file[path][k] = v
            h5file.close()


    @classmethod
    def fromJSON(cls, filepath, **kwargs):
        '''
        Create a DataModel from a JSON-encoded data file.
        Not compatible with SpacePy readJSONheadedASCII function.
        Attributes are not available without SpacePy.
        '''
        data_file = open(filepath, mode='r')
        dictionary = dict({'/': json_spacedata_decoder(json.load(data_file))})
        data_file.close()
        return cls(template=dictionary)


    def toJSON(self, filepath, **kwargs):
        '''
        Save this DataModel to a JSON-encoded data file.
        Not compatible with SpacePy toJSONheadedASCII function.
        Attributes are not available without SpacePy.
        '''
        data_file = open(filepath, mode='w')
        json.dump(self['/'], data_file, default=json_handler)
        data_file.close()
            

    @classmethod
    def fromCSV(cls, filepath, **kwargs):
        '''
        Create a DataModel from a CSV-encoded data file.
        Data arrays are column-based (each row is one entry).
        Does not support attributes.
        '''
        with_hdr = True
        if 'header' in kwargs:
            with_hdr = bool(kwargs['header'])
        fields = []
        data_model = cls()
        data_file = open(filepath, mode='r')
        for line in data_file:
            if with_hdr:
                with_hdr = False
                fields = [l.strip() for l in line.split(',')]
                continue
            data = [l.strip() for l in line.split(',')]
            for i, k in enumerate(fields):
                if not k in data_model.keys():
                    data_model[k] = []
                data_model[k].append(data[i])
        return data_model


    def toCSV(self, filepath, **kwargs):
        '''
        Save this DataModel to a CSV-encoded data file.
        Data arrays are column-based (each row is one entry).
        Does not support attributes.
        '''
        with_hdr = True
        if 'header' in kwargs:
            with_hdr = bool(kwargs['header'])
        data_file = open(filepath, mode='w')
        if with_hdr:
            data_file.write(','.join(self.keys()) + '\n')
        wrote = True
        line_num = 0
        while wrote:
            wrote = False
            val_list = []
            for v in self.values():
                try:
                    val_list.append(str(v[line_num]))
                    wrote = True
                except IndexError:
                    val_list.append('')
            line_num += 1
            if wrote:
                data_file.write(','.join(val_list) + '\n')
        data_file.close()
            


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
