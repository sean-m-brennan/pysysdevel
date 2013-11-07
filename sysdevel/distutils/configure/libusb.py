
import platform

from ..prerequisites import *
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install USB library
    """
    def __init__(self):
        lib_config.__init__(self, "usb", "usb.h", debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '1.0.9'
            major = '.'.join(version.split('.')[:2])
            website = ('http://prdownloads.sourceforge.net/project/libusb/',
                       'libusb-' + major + '/libusb-' + version + '/')
            if locally or 'windows' in platform.system().lower():
                src_dir = 'libusb-' + str(version)
                archive = src_dir + '.tar.bz2'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('USB', website,
                               brew='libusb', port='libusb-devel',
                               deb='libusb-dev', rpm='libusb-devel')
            if not self.is_installed(environ, version):
                raise Exception('USB installation failed.')
