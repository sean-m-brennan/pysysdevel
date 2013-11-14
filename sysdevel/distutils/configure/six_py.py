
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install six (Python 2 and 3 compatibility utilities)
    """
    def __init__(self):
        py_config.__init__(self, 'six', '1.4.1', debug=True)


