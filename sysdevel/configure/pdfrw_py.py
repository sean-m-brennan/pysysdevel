
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install pdfrw
    """
    def __init__(self):
        py_config.__init__(self, 'pdfrw', '0.1', debug=False)
