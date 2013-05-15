
import math

import raphael.min.js

from pyjamas.ui.SimplePanel import SimplePanel
from pyjamas.raphael.raphael import Raphael


class Plotter(SimplePanel):
    def __init__(self, width=800, height=600, color=0.5):
        SimplePanel.__init__(self)
        self.color = color
        self.series = []
        self.canvas = Raphael(width, height)   
        self.add(self.canvas)

    def update(self, history):
        self.series = history
        self.draw()

    def draw(self):
        for s in self.series:
            if 'zes' in s:
                self.plot3d(s['xes'], s['ys'], s['zes'],
                            s['series'], s['labels'])
            else:
                self.plot2d(s['xes'], s['ys'], s['series'], s['labels'])


    def plot2d(self, x_values, y_values, series, labels):
        pass #FIXME


    def plot3d(self, x_values, y_values, z_values, series, labels):
        pass #FIXME
