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


class UnknownModelException(Exception):
    def __init__(self, explain):
        Exception.__init__(self)
        self.what = explain

    def __str__(self):
        return 'Unknown model ' + self.what



##############################

class DataModel(dict):
    '''
    Model of Model-View-Controller pattern. Container for data updates by
    multiple controllers, read by viewer for display.
    '''

    date_format = '%Y-%m-%d'
    time_format = '%H:%M:%S'
    datetime_sep = 'T'
    datetime_tz = 'Z'
    datetime_format = date_format + datetime_sep + time_format + datetime_tz

    def __init__(self):
        dict.__init__(self)
        self._pipeline = dict()
        self._index = 0

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
    def __init__(self, *args, **kwargs):
        DataViewer.__init__(self, **kwargs)
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
