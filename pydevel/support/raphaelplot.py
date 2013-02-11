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

## Requires raphael.js

import math

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
