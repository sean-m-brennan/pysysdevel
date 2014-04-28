
import platform

from sysdevel.distutils.prerequisites import autotools_install_without_fetch, global_install
from sysdevel.distutils.fetching import fetch, unarchive
from sysdevel.distutils.configuration import lib_config

class configuration(lib_config):
    """
    Find/install libarchive
    """
    def __init__(self):
        lib_config.__init__(self, "archive", "archive.h", debug=False)


    def download(self, environ, version, strict=False):
        if version is None:
            version = '3.1.2'
        website = 'http://libarchive.org/downloads/'
        src_dir = 'libarchive-' + str(version)
        archive = src_dir + '.tar.gz'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if locally or 'windows' in platform.system().lower():
                src_dir = self.download(environ, version, strict)
                autotools_install_without_fetch(environ, src_dir, locally)
            else:
                global_install('Archive', None,
                               brew='libarchive', port='libarchive',
                               deb='libarchive-dev', rpm='libarchive-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('libarchive installation failed.')
