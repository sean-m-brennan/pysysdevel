
import platform

from ..prerequisites import autotools_install, global_install
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install GLFW
    """
    def __init__(self):
        lib_config.__init__(self, "glfw", "glfw3.h", debug=False)


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if version is None:
                version = '3.0.1'
            website = ('http://downloads.sourceforge.net/project/glfw/',
                       'glfw/' + str(version) + '/')
            if locally or 'windows' in platform.system().lower():
                src_dir = 'glfw-' + str(version)
                archive = src_dir + '.zip'
                #TODO this is a CMake build
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('GLFW', website,
                               brew='glfw', port='glfw-devel',
                               deb='libglfw-dev', rpm='glfw-devel')
                #TODO glfw package on CentOS/RHEL
            if not self.is_installed(environ, version, strict):
                raise Exception('GLFW installation failed.')
