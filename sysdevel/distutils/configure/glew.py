
import platform

from ..prerequisites import autotools_install, global_install
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install GLEW
    """
    def __init__(self):
        lib_config.__init__(self, "GLEW", "glew.h", debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '1.10.0'
            website = ('http://downloads.sourceforge.net/project/glew/',
                       'glew/' + str(version) + '/')
            if locally or 'windows' in platform.system().lower():
                src_dir = 'glew-' + str(version)
                archive = src_dir + '.tar.gz'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('GLEW', website,
                               brew='glew', port='glew-devel',
                               deb='libglew-dev', rpm='glew-devel')
            if not self.is_installed(environ, version):
                raise Exception('GLEW installation failed.')
