# -*- coding: utf-8 -*-
"""
Custom events
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

import gui_select


(FATAL, ERROR, WARNING, INFO, DEBUG, NOTICE, MESSAGE) = range(7)
primary_msgs = ['fatal', 'error', 'warning', 'info', 'debug',
                'notice', 'message']

(OK, CANCEL, INFORMATION, WARNING, QUESTION, ERROR) = range(6)

class Event(object):
    """
    Custom events
    """
    def __init__(self, string, ident=NOTICE, context=None, tpl=()):
        self._msg_id = ident
        self._string = string
        self._context = context
        self._tuple = tpl

    def GetId(self):
        return self._msg_id

    def GetText(self):
        return self._string

    def GetContext(self):
        return self._context

    def GetTuple(self):
        return self._tuple

    def Post(self, rcvr):
        raise NotImplementedError



def EventFactory(string, ident=NOTICE, context=None, tpl=()):
    backend = gui_select.BACKEND

    if backend == gui_select.WX:
        import wx_events
        return wx_events.wxEvent(string, ident, context, tpl)
    elif backend == gui_select.GTK:
        import gtk_events
        return gtk_events.gtkEvent(string, ident, context, tpl)
    ## TODO: other backends' events
    else:
        import txt_events
        return txt_events.txtEvent(string, ident, context, tpl)
