
from sysdevel.util import *
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install Python serial package
    """
    def __init__(self):
        py_config.__init__(self, 'serial', '2.6', debug=False)


    def is_installed(self, environ, version):
        try:
            import serial
            ver = serial.VERSION
            if compare_versions(ver, version) == -1:
                return self.found
            self.found = True
        except:
            pass
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            website = 'https://pypi.python.org/packages/source/p/pyserial/'
            if version is None:
                version = self.version
            src_dir = 'pyserial-' + str(version)
            archive = src_dir + '.tar.gz' 
            install_pypkg(src_dir, website, archive, locally=locally)
            if not self.is_installed(environ, version):
                raise Exception(self.pkg + ' installation failed.')
