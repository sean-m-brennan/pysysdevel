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

"""
Custom events
"""

import gui_select


(FATAL, ERROR, WARNING, INFO, DEBUG, NOTICE, MESSAGE) = list(range(7))
primary_msgs = ['fatal', 'error', 'warning', 'info', 'debug',
                'notice', 'message']

(OK, CANCEL, INFORMATION, WARNING, QUESTION, ERROR) = list(range(6))

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
