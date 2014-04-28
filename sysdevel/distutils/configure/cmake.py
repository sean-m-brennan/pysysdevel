
from sysdevel.distutils.prerequisites import global_install, major_minor_version
from sysdevel.distutils.configuration import prog_config

class configuration(prog_config):
    """
    Find/install CMake
    """
    def __init__(self):
        prog_config.__init__(self, 'cmake', debug=False)


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if version is None:
                version = '2.8.10.2'
            website = ('http://www.cmake.org/',
                       'files/v' + major_minor_version(version) + '/')
            #TODO no local install
            global_install('CMake', website,
                           winstaller='cmake-' + str(version) + '-win32-x86.exe',
                           brew='cmake', port='cmake', deb='cmake', rpm='cmake')
            if not self.is_installed(environ, version, strict):
                raise Exception('CMake installation failed.')
