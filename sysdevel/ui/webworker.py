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
WebWorker support for pyjamas 
"""

# pylint: disable=F0401

from __pyjamas__ import JS
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
        try:
            is_mod = isinstance(module_or_function, basestring)
        except NameError:
            is_mod = isinstance(module_or_function, str)
        if is_mod:
            self.module = module_or_function
        else:
            self.function = module_or_function
        self.callback = callback
        self._wk = None
        if _worker_supported():
            if self.module:
                JS("""@{{self}}._wk = new $wnd.Worker(@{{self.module}} + '.js');""")
            elif self.function:
                JS("""@{{self}}._wk = new $wnd.Worker('webworker_helper.js');""")
                self._wk.postMessage(self.function.__name__)
            self._wk.onmessage = self.onMessage
            self._wk.onerror = self.onError


    def run(self, data):
        if self._wk is None:
            self.callback(self.module.onMessage(data))
        else:
            self._wk.postMessage(data)


    def onError(self, evt):
        log.error('WebWorker error: ' + evt)


    def onMessage(self, evt):
        self.callback(evt.data)
