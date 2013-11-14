
from ..prerequisites import global_install
from ..configuration import prog_config

class configuration(prog_config):
    """
    Find/install CMake
    """
    def __init__(self):
        prog_config.__init__(self, 'cmake', debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '2.8.10.2'
            website = ('http://www.cmake.org/',
                       'files/v' + major_minor_version(version) + '/')
            ## FIXME no local install
            global_install('CMake', website,
                           winstaller='cmake-' + str(version) + '-win32-x86.exe',
                           brew='cmake', port='cmake', deb='cmake', rpm='cmake')
            if not self.is_installed(environ, version):
                raise Exception('CMake installation failed.')
