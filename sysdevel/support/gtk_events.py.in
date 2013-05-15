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
