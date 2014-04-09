
import platform

from ..prerequisites import autotools_install_without_fetch, global_install
from ..fetching import fetch, unarchive
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install CPP unit test library
    """
    def __init__(self):
        lib_config.__init__(self, "cppunit", "TestCaller.h", debug=False)


    def download(self, environ, version, strict=False):
        if version is None:
            version = '1.12.1'
        website = 'http://downloads.sourceforge.net/cppunit/'
        src_dir = 'cppunit-' + str(version)
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
                global_install('CppUnit', None,
                               brew='cppunit', port='cppunit',
                               deb='libcppunit-dev', rpm='cppunit-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('CppUnit installation failed.')
