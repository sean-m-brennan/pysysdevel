
import platform

from sysdevel.distutils.prerequisites import autotools_install_without_fetch, global_install
from sysdevel.distutils.fetching import fetch, unarchive
from sysdevel.distutils.configuration import lib_config

class configuration(lib_config):
    """
    Find/install GLFW
    """
    def __init__(self):
        lib_config.__init__(self, "glfw", "glfw3.h", debug=False)


    def download(self, environ, version, strict=False):
        if version is None:
            version = '3.0.1'
        website = 'http://downloads.sourceforge.net/project/glfw/glfw/' + \
                  str(version) + '/'
        src_dir = 'glfw-' + str(version)
        archive = src_dir + '.zip'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if locally or 'windows' in platform.system().lower():
                src_dir = self.download(environ, version, strict)
                #TODO this is a CMake build
                autotools_install_without_fetch(environ, src_dir, locally)
            else:
                global_install('GLFW', None,
                               brew='glfw', port='glfw-devel',
                               deb='libglfw-dev', rpm='glfw-devel')
                #TODO glfw package on CentOS/RHEL
            if not self.is_installed(environ, version, strict):
                raise Exception('GLFW installation failed.')
