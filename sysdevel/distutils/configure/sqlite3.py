
import platform

from ..prerequisites import autotools_install, global_install
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install SQLite3
    """
    def __init__(self):
        lib_config.__init__(self, "sqlite3", "sqlite3.h", debug=False)


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if version is None:
                version = '3071502'
            website = ('http://sqlite.org/', )
            if locally or 'windows' in platform.system().lower():
                src_dir = 'sqlite-autoconf-' + str(version)
                archive = src_dir + '.tar.gz'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('SQLite3', website,
                               brew='sqlite', port='sqlite3',
                               deb='libsqlite-dev', rpm='sqlite-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('SQLite3 installation failed.')
