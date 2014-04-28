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
# pylint: disable=W0105
"""
Textual User Interface
"""

import sys

from sysdevel.ui import gui, txt_events


##############################

class TXT_GUI(gui.GUI):
    # pylint: disable=W0613
    def __init__(self, impl_mod, parent, resfile=None, has_log=True):
        gui.GUI.__init__(self)

        self.is_running = False
        try:
            __import__(self.implementation)
            impl = sys.modules[self.implementation]
            impl.txtSetup(self)
        except Exception:  # pylint: disable=W0703
            sys.stderr.write('Application ' + self.implementation +
                             ' not enabled/available\n' +
                             str(sys.exc_info()[1]) + '\n')
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

