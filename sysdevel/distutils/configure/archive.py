
import platform

from ..prerequisites import autotools_install, global_install
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install libarchive
    """
    def __init__(self):
        lib_config.__init__(self, "archive", "archive.h", debug=False)


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if version is None:
                version = '3.1.2'
            website = ('http://libarchive.org/', 'downloads/')
            if locally or 'windows' in platform.system().lower():
                src_dir = 'libarchive-' + str(version)
                archive = src_dir + '.tar.gz'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('Archive', website,
                               brew='libarchive', port='libarchive',
                               deb='libarchive-dev', rpm='libarchive-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('libarchive installation failed.')
