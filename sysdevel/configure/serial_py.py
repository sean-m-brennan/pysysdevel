
from sysdevel.util import *
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install Python serial package
    """
    def __init__(self):
        py_config.__init__(self, 'serial', '2.6', debug=False)


    def is_installed(self, environ, version):
        try:
            import serial
            ver = serial.VERSION
            if compare_versions(ver, version) == -1:
                return self.found
            self.found = True
        except:
            pass
        return self.found
