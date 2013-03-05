# -*- coding: utf-8 -*-
"""
Textual User Interface
"""
#**************************************************************************
# $Revision: 1.2 $
# $Author: brennan $
# $Date: 2012/06/19 18:44:48 $
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

import sys, os, time, threading

import gui, txt_events


##############################

class TXT_GUI(gui.GUI):
    def __init__(self, impl_mod, parent, resfile=None, has_log=True):
        gui.GUI.__init__(self)

        self.is_running = False
        try:
            __import__(self.implementation)
            impl = sys.modules[self.implementation]
            impl.txtSetup(self)
        except Exception, e:
            sys.stderr.write('Application ' + self.implementation +
                             ' not enabled/available\n' + str(e) + '\n')
            sys.exit(1)


    def Run(self):
        self.is_running = True
        try:
            while self.is_running:
                evt = txt_events.pop_evt_queue(0.5) # half second timeout
                if evt:
                    evt.Handle()
        except KeyboardInterrupt:
            self.onExit()


    def onExit(self):
        self.is_running = False
        self.app.log.info('Exiting.')
        self.app.Stop()
        sys.exit(0)

    def onHelp(self):
        pass

    def onAbout(self):
        pass

    def onNotice(self, txt):
        pass

    def onMessage(self, txt, tpl):
        pass
    

## end TXT_GUI
##############################

