
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install Shapely
    """
    def __init__(self):
        py_config.__init__(self, 'Shapely', '1.2.16',
                           dependecies=['geos'], debug=False)
