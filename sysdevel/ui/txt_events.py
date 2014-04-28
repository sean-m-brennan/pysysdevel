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
Custom single-thread event handling
"""

import Queue

from sysdevel.ui import events


## General asynchronous event facility ##########
__GenericEventList__ = Queue.Queue()

def pop_evt_queue(timeout=None):
    try:
        evt = __GenericEventList__.get(True, timeout)
    except Queue.Empty:
        return None
    try:
        __GenericEventList__.task_done()
    except ValueError:
        pass
    return evt


class genericAsynchEventType(object):
    def __init__(self):
        self.queue = __GenericEventList__
        self.function = None

    def Bind(self, _, fctn):
        self.function = fctn


class genericAsynchEvent(object):
    def __init__(self, evt_t):
        self.etype = evt_t

    def Post(self, _):
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
