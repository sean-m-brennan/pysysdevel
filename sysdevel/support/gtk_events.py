"""
Copyright 2013.  Los Alamos National Security, LLC. This material was
produced under U.S. Government contract DE-AC52-06NA25396 for Los
Alamos National Laboratory (LANL), which is operated by Los Alamos
National Security, LLC for the U.S. Department of Energy. The
U.S. Government has rights to use, reproduce, and distribute this
software.  NEITHER THE GOVERNMENT NOR LOS ALAMOS NATIONAL SECURITY,
LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR ASSUMES ANY LIABILITY
FOR THE USE OF THIS SOFTWARE.  If software is modified to produce
derivative works, such modified software should be clearly marked, so
as not to confuse it with the version available from LANL.

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
Custom GTK events
"""

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
