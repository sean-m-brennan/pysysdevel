
from sysdevel.util import *
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install networkx package
    """
    def __init__(self):
        py_config.__init__(self, 'networkx', '1.7', debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = self.version
            website = 'http://networkx.lanl.gov/download/networkx/'
            src_dir = 'networkx-' + str(version)
            archive = src_dir + '.tar.gz'
            install_pypkg(src_dir, website, archive, locally=locally)
            if not self.is_installed(environ, version):
                raise Exception('networkx installation failed.')
