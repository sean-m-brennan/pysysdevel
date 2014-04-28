
from sysdevel.distutils.configuration import nodejs_config

class configuration(nodejs_config):
    """
    Find/install WebGL module for Node.js
    """
    def __init__(self):
        nodejs_config.__init__(self, 'WebGL',
                               dependencies=['glew', 'glfw', 'anttweakbar',
                                             'freeimage'], debug=True)
