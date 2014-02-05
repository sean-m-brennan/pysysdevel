
import sys

from ..prerequisites import compare_versions, install_pypkg
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install Python image library
    """
    def __init__(self):
        py_config.__init__(self, 'PIL', '1.1.7', debug=False)


    def is_installed(self, environ, version=None):
        try:
            import PIL.Image
            ver = PIL.Image.VERSION
            if compare_versions(ver, version) == -1:
                return self.found
            self.found = True
        except ImportError:
            if self.debug:
                print(sys.exc_info()[1])
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            website = 'http://effbot.org/downloads/'
            if version is None:
                version = self.version
            src_dir = 'Imaging-' + str(version)
            archive = src_dir + '.tar.gz'
            install_pypkg(src_dir, website, archive, locally=locally)
            if not self.is_installed(environ, version):
                raise Exception('PIL.Image installation failed.')
