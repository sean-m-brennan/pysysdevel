
from ..prerequisites import *
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install keyring
    """
    def __init__(self):
        py_config.__init__(self, 'keyring', '1.4',
                           #dependencies=['pytest-runner',],
                           debug=False)
