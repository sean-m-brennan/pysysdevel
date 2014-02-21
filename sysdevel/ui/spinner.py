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

import math

# pylint: disable=F0401,E1101

from pyjamas.Timer import Timer
from pyjamas import Window
from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.PopupPanel import PopupPanel
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.raphael.raphael import Raphael
from pyjamas.ui.HTML import HTML


class Spinner(PopupPanel):
    def __init__(self, text=''):
        PopupPanel.__init__(self)

        self.width       = 15
        self.r1          = 35
        self.r2          = 60
        self.cx          = self.r2 + self.width
        self.cy          = self.r2 + self.width
        self.numSectors  = 12
        self.size        = self.r2*2 + self.width*2
        self.speed       = 1.5  # seconds per rotation
        self._timer      = None

        self.canvas = Raphael(self.size, self.size)
        self.sectors = []
        self.opacity = []
        vp = VerticalPanel()
        vp.add(self.canvas)
        blurb = HTML(text)
        blurb.setStyleAttribute('text-align', 'center')
        vp.add(blurb)
        self.add(vp)


    def draw(self):
        colour           = "#000000"
        beta             = 2 * math.pi / self.numSectors

        pathParams = {'stroke'         : colour,
                      'stroke-width'   : self.width,
                      'stroke-linecap' : "round"}

        for i in range(self.numSectors):
            alpha = beta * i - math.pi/2
            cos   = math.cos(alpha)
            sin   = math.sin(alpha)
            data  = ','.join(['M',
                              str(self.cx + self.r1 * cos),
                              str(self.cy + self.r1 * sin),
                              'L',
                              str(self.cx + self.r2 * cos),
                              str(self.cy + self.r2 * sin)])
            path  = self.canvas.path(data=data, attrs=pathParams)
            self.opacity.append(1.0 * i / self.numSectors )
            self.sectors.append(path)

        period = (self.speed * 1000) / self.numSectors
        self._timer = Timer(notify=self)
        self._timer.scheduleRepeating(period)        


    def onTimer(self, _):
        self.opacity.insert(0, self.opacity.pop())
        for i in range(self.numSectors):
            self.sectors[i].setAttr("opacity", self.opacity[i])


__spinner = None

def start_spinner(container, run_str='Processing<br>Please wait...'):
    global __spinner  # pylint: disable=W0603
    __spinner = Spinner(run_str)
    RootPanel().add(__spinner)
    center = (Window.getClientWidth() - __spinner.size) / 2
    middle = Window.getClientHeight() / 3
    __spinner.setPopupPosition(center, middle)
    __spinner.show()
    __spinner.draw()
    container.setStyleAttribute('opacity', '0.3')


def quit_spinner(container):
    if __spinner:
        __spinner.hide()
    container.setStyleAttribute('opacity', '1.0')
