"""
Custom events
"""

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
