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

import sys

SPLASH_DURATION        = 1000  ## in milliseconds


class GUI(object):
    def __init__(self, impl_mod, parent):
        self.app = parent
        self.implementation = impl_mod

    def Run(self):
        raise NotImplementedError

    def onExit(self):
        raise NotImplementedError

    def onFatal(self):
        self.app.log.info("Fatal exception encountered. Exiting.")
        sys.exit(1)

    def onError(self, txt):
        self.app.log.error(txt)

    def onWarning(self, txt):
        self.app.log.warning(txt)

    def onInfo(self, txt):
        self.app.log.info(txt)
            
    def onDebug(self, txt):
        self.app.log.debug(txt)



##############################
## function wrapper to add class methods at runtime

class transplant(object):
    def __init__(self, method, host, method_name=None):
        self.host = host
        self.method = method
        setattr(host, method_name or method.__name__, self)

    def __call__(self, *args, **kwargs):
        nargs = [self.host]
        nargs.extend(args)
        return apply(self.method, nargs, kwargs)


