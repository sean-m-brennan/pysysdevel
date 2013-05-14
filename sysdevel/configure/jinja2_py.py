
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install Jinja2
    """
    def __init__(self):
        py_config.__init__(self, 'Jinja2', '2.6', debug=False)
