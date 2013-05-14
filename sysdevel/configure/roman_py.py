
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install Roman
    """
    def __init__(self):
        py_config.__init__(self, 'roman', '1.4.0', debug=False)

