
import platform

from ..prerequisites import autotools_install, global_install
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install GNU Scientific Library
    """
    def __init__(self):
        lib_config.__init__(self, "gsl", "gsl_types.h", debug=False)


    def is_installed(self, environ, version=None):
        lib_config.is_installed(self, environ, version)
        self.environment['GSL_LIBRARIES'] += ['gslcblas']


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '1.15'
            website = ('ftp://ftp.gnu.org/gnu/gsl/',)
            if locally or 'windows' in platform.system().lower():
                src_dir = 'gsl-' + str(version)
                archive = src_dir + '.tar.gz'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('GSL', website,
                               brew='gsl', port='gsl-devel',
                               deb='libgsl-dev', rpm='gsl-devel')
            if not self.is_installed(environ, version):
                raise Exception('GSL installation failed.')
