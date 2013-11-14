
import sys

from ..configuration import py_config

class configuration(py_config):
    """
    If we're running Python 2.4/5, substitute in this patched urllib2. 
    """
    def __init__(self):
        py_config.__init__(self, 'httpsproxy_urllib2', '1.0', debug=False)


    def is_installed(self, environ, version):
        if sys.version_info < (2, 6):
            ## Cannot detect if this is already present
            self.found = False
        else:
            ## Not needed for Python 2.6+
            self.found = True
        return self.found


    def install(self, environ, version, locally=True):
        py_config.install(self, environ, version, locally)
        reload(urllib2)
        reload(httplib)
