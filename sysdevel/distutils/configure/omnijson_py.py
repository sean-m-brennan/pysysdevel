
from ..prerequisites import *
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install omnijson
    """
    def __init__(self):
        py_config.__init__(self, 'omnijson', '0.1.2', debug=False)
