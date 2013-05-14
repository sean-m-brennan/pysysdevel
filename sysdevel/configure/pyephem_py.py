
from sysdevel.util import *
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install Pyephem
    """
    def __init__(self):
        py_config.__init__(self, 'ephem', '3.7.5.1', debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            website = 'http://pypi.python.org/packages/source/p/pyephem/'
            if version is None:
                version = self.version
            src_dir = 'pyephem-' + str(version)
            archive = src_dir + '.tar.gz'
            install_pypkg(src_dir, website, archive, locally=locally)
            if not self.is_installed(environ, version):
                raise Exception('pyephem installation failed.')
