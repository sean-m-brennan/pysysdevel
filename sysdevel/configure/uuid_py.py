
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install Uuid
    """
    def __init__(self):
        py_config.__init__(self, 'uuid', '1.30', debug=False)
