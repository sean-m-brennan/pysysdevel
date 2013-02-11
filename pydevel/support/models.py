# Model factories and base classes
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


class UnknownModelException(Exception):
    def __init(self, what):
        self.what = what

    def __str__(self):
        return 'Unknown model ' + what



class MVC(object):
    def __init__(self):
        pass

    @staticmethod
    def validate(kwargs):
        raise NotImplementedError()



##############################

class DataModel(MVC):
    pass



##############################

class DataController(MVC):
    def control(self, data_model):
        raise NotImplementedError()




##############################

class DataViewer(MVC):
    def view(self, data_model):
        raise NotImplementedError()



class GenericPlot(DataViewer):
    '''
    General graphing viewer, may display several PlotSeries.
    Usage::

        for datum in data:
            plot.view(datum)
        plot.plot()

    '''
    def __init__(self, axes=2):
        self.chart_title = 'Chart'
        self.axes = axes
        self.series = []


    def __dict__(self):
        return {
            'chart_title': self.chart_title,
            'series': [s.__dict__() for s in self.series],
            }

    def view(self, data_model):
        s = PlotSeries(self.axes)
        s.view(data_model)  ## but this is unimplemented
        self.series.append(s)


    def plot(self):
        import pylab as plot

        for s in self.series:  ## FIXME single figure?
            plot.figure()
            if p.axes == 3:
                plot.plot(p.x_values, p.y_values, p.z_values)
                plot.xlabel(p.labels[0])
                plot.ylabel(p.labels[1])
                plot.zlabel(p.labels[2])
            else:
                plot.plot(p.x_values, p.y_values)
                plot.xlabel(p.labels[0])
                plot.ylabel(p.labels[1])
            plot.title(p.series_name)
            plot.show()



class PlotSeries(DataViewer):
    '''
    General plotting, represents a single two or three axis data series.
    '''
    def __init__(self, axes=2):
        self.name = 'Series'
        self.axes = axes
        self.x_values = []
        self.y_values = []
        self.z_values = []
        self.labels = ['', '', '']

    def __dict__(self):
        if self.axes == 3:
            return {
                'name': self.name,
                'x_values': self.x_values,
                'x_ticks': self.x_ticks,
                'y_values': self.y_values,
                'y_ticks': self.y_ticks,
                'z_values': self.z_values,
                'z_ticks': self.z_ticks,
                'labels': self.labels,
                }
        else:
            return {
                'name': self.name,
                'x_values': self.x_values,
                'x_ticks': self.x_ticks,
                'y_values': self.y_values,
                'y_ticks': self.y_ticks,
                'labels': self.labels,
                }

    def view(self, data_model):
        '''
        Given a DataModel, compute the plot values.
        '''
        raise NotImplementedError()


    @property
    def x_ticks(self):
        if len(self.x_values) < 1:
            return [-1, 1]
        lo = int(min(self.x_values))-1
        hi = int(max(self.x_values))+1
        if hi - lo < 10:
            step = 1
        else:
            step = (hi - lo) / 10
        try:
            return range(lo, hi, step)
        except ValueError:
            return range(lo, hi)

    @property
    def y_ticks(self):
        if len(self.y_values) < 1:
            return [-1, 1]
        lo = int(min(self.y_values))-1
        hi = int(max(self.y_values))+1
        if hi - lo < 10:
            step = 1
        else:
            step = (hi - lo) / 10
        try:
            return range(lo, hi, step)
        except ValueError:
            return range(lo, hi)

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
            return range(lo, hi, step)
        except ValueError:
            return range(lo, hi)
