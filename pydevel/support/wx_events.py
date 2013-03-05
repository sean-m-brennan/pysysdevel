# -*- coding: utf-8 -*-
"""
Custom event handling for wxPython
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

import events

try:
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    import wx
    warnings.resetwarnings()
    
    mywxCmdEvent = wx.NewEventType()
    wxCmdEvent = wx.PyEventBinder(mywxCmdEvent, 1)

    class wxEvent(events.Event, wx.PyCommandEvent):
        """
        Custom WX events
        """
        OK          = wx.OK
        CANCEL      = wx.CANCEL
        INFORMATION = wx.ICON_INFORMATION
        WARNING     = wx.ICON_EXCLAMATION
        QUESTION    = wx.ICON_QUESTION
        ERROR       = wx.ICON_ERROR

        def __init__(self, string, ident=events.NOTICE, context=None, tpl=(),
                     evt=mywxCmdEvent):
            wx.PyCommandEvent.__init__(self, evt, ident)
            events.Event.__init__(self, string, ident, context, tpl)

        def Post(self, rcvr):
            wx.PostEvent(rcvr, self)


except:
    pass
