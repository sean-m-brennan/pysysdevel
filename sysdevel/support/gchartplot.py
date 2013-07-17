"""
Copyright 2013.  Los Alamos National Security, LLC. This material was
produced under U.S. Government contract DE-AC52-06NA25396 for Los
Alamos National Laboratory (LANL), which is operated by Los Alamos
National Security, LLC for the U.S. Department of Energy. The
U.S. Government has rights to use, reproduce, and distribute this
software.  NEITHER THE GOVERNMENT NOR LOS ALAMOS NATIONAL SECURITY,
LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR ASSUMES ANY LIABILITY
FOR THE USE OF THIS SOFTWARE.  If software is modified to produce
derivative works, such modified software should be clearly marked, so
as not to confuse it with the version available from LANL.

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

import math

## no js dependency

from pyjamas import logging
log = logging.getConsoleLogger()

from pyjamas.ui.SimplePanel import SimplePanel
from pyjamas.chart import GChart
from pyjamas.chart import GChartConsts
from pyjamas.Canvas.GWTCanvas import GWTCanvas


class GWTCanvasBasedCanvasFactory(object):
    def create(self):
        return GWTCanvas()


class Plotter(SimplePanel):
    def __init__(self, width=800, height=600, colors=['red', 'blue', 'green']):
        SimplePanel.__init__(self)
        GChart.setCanvasFactory(GWTCanvasBasedCanvasFactory())
        self.colors = colors
        self.series = []
        self.canvas = GChart.GChart()
        self.canvas.setChartSize(width, height)
        self.canvas.setBorderStyle("none")
        self.canvas.getXAxis().setHasGridlines(True)
        self.canvas.getYAxis().setHasGridlines(True)
        self.add(self.canvas)

    def update(self, plot):
        self.series = plot['series']
        log.debug('PLOTTING ' + plot['chart_title'])
        self.draw()


    def draw(self):
        idx = 0
        for s in self.series:
            if 'z_values' in s.keys():
                self.plot3d(idx, s['name'], s['labels'],
                            s['x_values'], s['y_values'], s['z_values'],
                            s['x_ticks'], s['y_ticks'], s['z_ticks'])
            else:
                self.plot2d(idx, s['name'], s['labels'],
                            s['x_values'], s['y_values'],
                            s['x_ticks'], s['y_ticks'])
            idx += 1
        self.canvas.update()


    def plot2d(self, num, series, labels, x_values, y_values, x_ticks, y_ticks):
        self.canvas.addCurve()
        self.canvas.getCurve().getSymbol().setFillSpacing(0)
        self.canvas.getCurve().setYAxis(GChartConsts.Y_AXIS)
        for idx in range(len(y_values)):
            self.canvas.getCurve().addPoint(x_values[idx], y_values[idx])
        self.canvas.getCurve().getSymbol().setFillThickness(1)
        #self.canvas.getCurve().getSymbol().setBackgroundColor(self.colors[num])
        self.canvas.getCurve().setLegendLabel(series)

        self.canvas.getXAxis().setAxisLabel(labels[0])
        self.canvas.getXAxis().setTickCount(len(x_ticks))
        self.canvas.getXAxis().setAxisMin(x_ticks[0])
        self.canvas.getXAxis().setAxisMax(x_ticks[-1])

        self.canvas.getYAxis().setAxisLabel(labels[1])
        self.canvas.getYAxis().setTickCount(len(y_ticks))
        self.canvas.getYAxis().setAxisMin(y_ticks[0])
        self.canvas.getYAxis().setAxisMax(y_ticks[-1])


    def plot2dplus(self, num, series, labels,
                   x_values, y_values, z_values, x_ticks, y_ticks):
        pass # FIXME 2D plot with a color range

    def plot3d(self, num, series, labels,
               x_values, y_values, z_values, x_ticks, y_ticks, z_ticks):
        pass #FIXME 3D plot
