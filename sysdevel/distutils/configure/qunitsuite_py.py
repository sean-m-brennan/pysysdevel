
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install QUnitSuite
    """
    def __init__(self):
        py_config.__init__(self, 'QUnitSuite', '0.3', debug=False)
