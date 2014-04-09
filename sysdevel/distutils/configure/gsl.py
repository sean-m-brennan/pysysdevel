
import platform

from ..prerequisites import autotools_install_without_fetch, global_install
from ..fetching import fetch, unarchive
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install GNU Scientific Library
    """
    def __init__(self):
        lib_config.__init__(self, "gsl", "gsl_types.h", debug=False)


    def is_installed(self, environ, version=None, strict=False):
        lib_config.is_installed(self, environ, version, strict)
        if self.found:
            self.environment['GSL_LIBRARIES'] += ['gslcblas']
            lib_file = self.environment['GSL_LIB_FILES'][0]
            pre, post = lib_file.split('gsl')
            self.environment['GSL_LIB_FILES'] += [pre + 'gslcblas' + post]
        return self.found


    def download(self, environ, version, strict=False):
        if version is None:
            version = '1.15'
        website = 'ftp://ftp.gnu.org/gnu/gsl/'
        src_dir = 'gsl-' + str(version)
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
                global_install('GSL', None,
                               brew='gsl', port='gsl-devel',
                               deb='libgsl-dev', rpm='gsl-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('GSL installation failed.')
