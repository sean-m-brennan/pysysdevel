
from ..prerequisites import *
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install Python USB package
    """
    def __init__(self):
        py_config.__init__(self, 'usb', '1.0.0a3',
                           dependencies=['libusb'], debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            website = 'http://pypi.python.org/packages/source/p/pyusb/'
            if version is None:
                version = self.version
            src_dir = 'pyusb-' + version
            archive = src_dir + '.tar.gz'
            install_pypkg(src_dir, website, archive, locally=locally)
            if not self.is_installed(environ, version):
                raise Exception('pyusb installation failed.')
