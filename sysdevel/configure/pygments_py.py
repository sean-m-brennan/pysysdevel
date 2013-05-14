
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install Pygments
    """
    def __init__(self):
        py_config.__init__(self, 'Pygments', '1.6', debug=False)
