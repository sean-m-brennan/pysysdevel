
import platform

from sysdevel.distutils.prerequisites import autotools_install_without_fetch, global_install
from sysdevel.distutils.fetching import fetch, unarchive
from sysdevel.distutils.configuration import lib_config

class configuration(lib_config):
    """
    Find/install GLEW
    """
    def __init__(self):
        lib_config.__init__(self, "GLEW", "glew.h", debug=False)


    def download(self, environ, version, strict=False):
        if version is None:
            version = '1.10.0'
        website = 'http://downloads.sourceforge.net/project/glew/' + \
                  'glew/' + str(version) + '/'
        src_dir = 'glew-' + str(version)
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
                global_install('GLEW', None,
                               brew='glew', port='glew-devel',
                               deb='libglew-dev', rpm='glew-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('GLEW installation failed.')
