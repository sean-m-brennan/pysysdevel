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

import math

from pyjamas.Timer import Timer
from pyjamas import Window
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


    def onTimer(self, timerID):
        self.opacity.insert(0, self.opacity.pop())
        for i in range(self.numSectors):
            self.sectors[i].setAttr("opacity", self.opacity[i])
