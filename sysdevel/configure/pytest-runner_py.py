
from sysdevel.util import *
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install pytest-runner
    """
    def __init__(self):
        py_config.__init__(self, 'pytest-runner', '2.0',
                           dependencies=['hgtools',], debug=False)
