
from ..prerequisites import compare_versions
from ..configuration import py_config
from .. import options

class configuration(py_config):
    """
    Find/install Euclid
    """
    def __init__(self):
        py_config.__init__(self, 'euclid', '0.01', debug=False)


    def is_installed(self, environ, version):
        try:
            import euclid
            ver = euclid.__revision__.split()[1]
            if compare_versions(ver, version) == -1:
                return self.found
            self.found = True
        except Exception:
            if self.debug:
                print(sys.exc_info()[1])
        return self.found
