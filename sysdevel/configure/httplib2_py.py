
from sysdevel.util import *
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install httplib2
    """
    def __init__(self):
        py_config.__init__(self, 'httplib2', '0.8', debug=False)


