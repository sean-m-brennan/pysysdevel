
import platform

from ..prerequisites import autotools_install, global_install
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install CPP unit test library
    """
    def __init__(self):
        lib_config.__init__(self, "cppunit", "TestCaller.h", debug=False)


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if version is None:
                version = '1.12.1'
            website = ('http://downloads.sourceforge.net/cppunit/',)
            if locally or 'windows' in platform.system().lower():
                src_dir = 'cppunit-' + str(version)
                archive = src_dir + '.tar.gz'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('CppUnit', website,
                               brew='cppunit', port='cppunit',
                               deb='libcppunit-dev', rpm='cppunit-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('CppUnit installation failed.')
