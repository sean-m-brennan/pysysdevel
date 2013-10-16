
from sysdevel.util import *
from sysdevel.configuration import py_config


class configuration(py_config):
    """
    Find/install Reportlab
    """
    def __init__(self):
        py_config.__init__(self, 'reportlab', '2.7', debug=False)
        ## NB: will not work with Python 2.4
        if sys.version_info < (2, 6):
            raise Exception('Reportlab is not supported ' +
                            'for Python versions < 2.6')


    def is_installed(self, environ, version):
        try:
            import reportlab
            ver = reportlab.Version
            if compare_versions(ver, version) == -1:
                return self.found
            self.found = True
        except Exception as e:
            if self.debug:
                print(e)
        return self.found
