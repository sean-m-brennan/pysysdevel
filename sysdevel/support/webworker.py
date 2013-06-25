"""
WebWorker support for pyjamas 
"""

from __pyjamas__ import JS
from pyjamas import Window
from pyjamas import logging
log = logging.getConsoleLogger()


def _worker_supported():
    return JS("""typeof $wnd.Worker === 'function'""")

if not _worker_supported():
    def postMessage(data):
        return data


class WebWorker(object):
    def __init__(self, module_or_function, callback):
        """
        Can take either a module name or a function:
          Module given must define an onMessage(event) function that
          uses the passed event.data and returns data via a postMessage call.
          Function given must be gloabl and implement onMessage as above.
        """
        self.module = self.function = None
        if isinstance(module_or_function, basestring):
            self.module = module_or_function
        else:
            self.function = module_or_function
        self.callback = callback
        if _worker_supported():
            if self.module:
                JS("""@{{self}}._wk = new $wnd.Worker(@{{self.module}} + '.js');""")
            elif self.function:
                JS("""@{{self}}._wk = new $wnd.Worker('webworker_helper.js');""")
                self._wk.postMessage(self.function.__name__)
            self._wk.onmessage = self.onMessage
            self._wk.onerror = self.onError
        else:
            self._wk = None


    def run(self, data):
        if self._wk is None:
            self.callback(self.module.onMessage(data))
        else:
            self._wk.postMessage(data)


    def onError(self, evt):
        log.error('WebWorker error: ' + evt)


    def onMessage(self, evt):
        self.callback(evt.data)
