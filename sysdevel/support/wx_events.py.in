"""
Custom event handling for wxPython
"""

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
