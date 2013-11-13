
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install Fuzzy
    """
    def __init__(self):
        py_config.__init__(self, 'Fuzzy', '1.0', debug=False)


    def is_installed(self, environ, version):
        try:
            import fuzzy
            ver = fuzzy.__version__
            check_version = False
            if hasattr(fuzzy, '__version__'):
                ver = fuzzy.__version__
                check_version = True
            elif hasattr(fuzzy, 'version'):
                ver = fuzzy.version
                check_version = True
            if check_version:
                if compare_versions(ver, version) == -1:
                    return self.found
            self.found = True
        except Exception:
            if self.debug:
                e = sys.exc_info()[1]
                print(e)
        return self.found
