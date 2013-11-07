
from ..prerequisites import *
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install hgtools
    """
    def __init__(self):
        py_config.__init__(self, 'hgtools', '3.0.2', debug=False)
