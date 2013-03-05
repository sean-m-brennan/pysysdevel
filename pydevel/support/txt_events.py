# -*- coding: utf-8 -*-
"""
Custom single-thread event handling
"""
#**************************************************************************
# $Revision: 1.1 $
# $Author: brennan $
# $Date: 2012/02/16 23:23:31 $
#**************************************************************************
#
# OFFICIAL USE ONLY, EXPORT CONTROLLED INFORMATION
# 
# This software includes technical information, the export of which is  
# restricted by the Arms Export Control Act (22 U.S.C. 2751, et seq.),  
# the Atomic Energy Act of 1954, as amended (42 U.S.C. 2077), or the  
# Export Administration Act of 1979, as amended (50 U.S.C. 2401, et  
# seq.). Violations of these laws may result in severe administrative,  
# civil, or criminal penalties.
# 
# Distribution authorized to U.S. Government agencies and their  
# contractors; other requests shall be approved by the cognizant DOE  
# Departmental Element.
# 
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

import sys
import Queue
import events


## General asynchronous event facility ##########
__GenericEventList__ = Queue.Queue()

def pop_evt_queue(timeout=None):
    try:
        evt = __GenericEventList__.get(True, timeout)
    except Queue.Empty:
        return None
    try:
        __GenericEventList__.task_done()
    except:
        pass
    return evt


class genericAsynchEventType(object):
    def __init__(self):
        self.queue = __GenericEventList__
        self.function = None

    def Bind(self, pid, fctn):
        self.function = fctn


class genericAsynchEvent(object):
    def __init__(self, evt_t):
        self.etype = evt_t

    def Post(self, rcvr):
        self.etype.queue.put(self)

    def Handle(self):
        self.etype.function(self)
    
    def Skip(self):
        pass



## Specific events ##########

txtCmdEvent = genericAsynchEventType()

class txtEvent(genericAsynchEvent, events.Event):
    """
    Custom events
    """
    (OK, CANCEL, INFORMATION, WARNING, QUESTION, ERROR) = range(6)

    def __init__(self, string, ident=events.NOTICE, context=None, tpl=()):
        genericAsynchEvent.__init__(self, txtCmdEvent)
        events.Event.__init__(self, string, ident, context, tpl)
