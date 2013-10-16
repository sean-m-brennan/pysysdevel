
from sysdevel.util import *
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install Euclid
    """
    def __init__(self):
        py_config.__init__(self, 'euclid', '0.01', debug=False)


    def is_installed(self, environ, version):
        set_debug(self.debug)
        try:
            import euclid
            ver = euclid.__revision__.split()[1]
            if compare_versions(ver, version) == -1:
                return self.found
            self.found = True
        except Exception as e:
            if self.debug:
                print(e)
        return self.found
