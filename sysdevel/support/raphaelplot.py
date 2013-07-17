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
