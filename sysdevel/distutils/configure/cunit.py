
import platform

from ..prerequisites import autotools_install_without_fetch, global_install
from ..fetching import fetch, unarchive
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install C unit test library
    """
    def __init__(self):
        lib_config.__init__(self, "cunit", "CUnit.h", debug=False)


    def download(self, environ, version, strict=False):
        if version is None:
            version = '2.1-2'
        website = 'http://downloads.sourceforge.net/project/cunit/' + \
                  'CUnit/' + str(version) + '/'
        src_dir = 'CUnit-' + str(version) + '-src'
        archive = src_dir + '-src.tar.bz2'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if locally or 'windows' in platform.system().lower():
                src_dir = self.download(environ, version, strict)
                autotools_install_without_fetch(environ, src_dir, locally)
            else:
                global_install('CUnit', None,
                               brew='cunit', port='cunit',
                               deb='libcunit1-dev', rpm='CUnit-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('CUnit installation failed.')
