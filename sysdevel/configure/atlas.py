
import platform

from sysdevel.util import *
from sysdevel.configuration import lib_config

class configuration(lib_config):
    """
    Find/install ATLAS library (includes libblas)
    """
    def __init__(self):
        lib_config.__init__(self, "atlas", "gsl_types.h", debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '3.10.1'
            website = ('http://downloads.sourceforge.net/project/math-atlas/',
                       'Stable/' + version + '/',)
            if locally or 'windows' in platform.system().lower():
                src_dir = 'atlas' + str(version)
                archive = src_dir + '.tar.bz2'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('ATLAS', website,
                               ## part of XCode
                               deb='libatlas-dev', rpm='atlas-devel')
            if not self.is_installed(environ, version):
                raise Exception('ATLAS installation failed.')
