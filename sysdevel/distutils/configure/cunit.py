
import platform

from ..prerequisites import *
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install C unit test library
    """
    def __init__(self):
        lib_config.__init__(self, "cunit", "CUnit.h", debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '2.1-2'
            website = ('http://downloads.sourceforge.net/project/cunit/',
                       'CUnit/' + str(version) + '/')
            if locally or 'windows' in platform.system().lower():
                src_dir = 'CUnit-' + str(version) + '-src'
                archive = src_dir + '-src.tar.bz2'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('CUnit', website,
                               brew='cunit', port='cunit',
                               deb='libcunit1-dev', rpm='CUnit-devel')
            if not self.is_installed(environ, version):
                raise Exception('CUnit installation failed.')
