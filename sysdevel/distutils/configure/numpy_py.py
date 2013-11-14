
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install numpy
    """
    def __init__(self):
        py_config.__init__(self, 'numpy', '1.8.0', debug=False)
