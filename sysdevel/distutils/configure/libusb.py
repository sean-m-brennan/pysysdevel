
import platform

from ..prerequisites import autotools_install_without_fetch, global_install
from ..fetching import fetch, unarchive
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install USB library
    """
    def __init__(self):
        lib_config.__init__(self, "usb", "usb.h", debug=False)


    def download(self, environ, version, strict=False):
        if version is None:
            version = '1.0.9'
        major = '.'.join(version.split('.')[:2])
        website = 'http://prdownloads.sourceforge.net/project/libusb/libusb-' +\
                  major + '/libusb-' + version + '/'
        src_dir = 'libusb-' + str(version)
        archive = src_dir + '.tar.bz2'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if locally or 'windows' in platform.system().lower():
                src_dir = self.download(environ, version, strict)
                autotools_install_without_fetch(environ, src_dir, locally)
            else:
                global_install('USB', None,
                               brew='libusb', port='libusb-devel',
                               deb='libusb-dev', rpm='libusb-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('USB installation failed.')
