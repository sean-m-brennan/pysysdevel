
from ..prerequisites import *
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install dateutil
    """
    def __init__(self):
        py_config.__init__(self, 'dateutil', '2.1', debug=True,
                           dependencies=['six'])


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = self.version
            website = 'http://pypi.python.org/packages/source/p/python-dateutil/'
            src_dir = 'python-dateutil-' + str(version)
            archive = src_dir + '.tar.gz' 
            install_pypkg(src_dir, website, archive, locally=locally)
