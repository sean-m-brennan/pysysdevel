
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install SQLAlchemy
    """
    def __init__(self):
        py_config.__init__(self, 'SQLAlchemy', '0.8.2', debug=False)
