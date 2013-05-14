
from sysdevel.util import *
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install Docutils
    """
    def __init__(self):
        py_config.__init__(self, 'docutils', '0.10', debug=False)
