# -*- coding: utf-8 -*-
"""
Custom GTK events
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
    ## Eliminate "PendingDeprecationWarning: The CObject type is marked Pending Deprecation in Python 2.7.  Please use capsule objects instead."
    warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
    import gtk
    import gobject
    warnings.resetwarnings()


    class gtkEvent(events.Event, gobject.GObject):
        """
        Custom GTK events
        """
        OK          = gtk.BUTTONS_OK
        CANCEL      = gtk.BUTTONS_CANCEL
        INFORMATION = gtk.MESSAGE_INFO
        WARNING     = gtk.MESSAGE_WARNING
        QUESTION    = gtk.MESSAGE_QUESTION
        ERROR       = gtk.MESSAGE_ERROR

        def __init__(self, string, ident=events.NOTICE, context=None, tpl=()):
            self.__gobject_init__()
            events.Event.__init__(self, string, ident, context, tpl)

        def Post(self, rcvr):
            self.connect(events.gse_msgs[self._msg_id],
                         rcvr.EventDistributor)
            self.emit(events.gse_msgs[self._msg_id])

    
    gobject.type_register(gtkEvent)


except:
    pass
