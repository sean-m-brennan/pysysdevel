
import platform

from ..prerequisites import autotools_install_without_fetch, global_install
from ..fetching import fetch, unarchive
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install SQLite3
    """
    def __init__(self):
        lib_config.__init__(self, "sqlite3", "sqlite3.h", debug=False)


    def download(self, environ, version, strict=False):
        if version is None:
            version = '3071502'
        website = 'http://sqlite.org/'
        src_dir = 'sqlite-autoconf-' + str(version)
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
                global_install('SQLite3', None,
                               brew='sqlite', port='sqlite3',
                               deb='libsqlite-dev', rpm='sqlite-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('SQLite3 installation failed.')
