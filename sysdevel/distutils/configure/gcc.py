
from ..prerequisites import *
from ..configuration import prog_config

class configuration(prog_config):
    """
    Find/fetch/install the GNU compiler collection
    """
    def __init__(self):
        prog_config.__init__(self, 'gcc', debug=False)


    def null(self):
        self.environment['GCC'] = None
        self.environment['GXX'] = None


    def is_installed(self, environ, version):
        set_debug(self.debug)
        try:
            gcc = find_program('gcc')
            gxx = find_program('g++')
            self.found = True
        except Exception as e:
            if self.debug:
                print(e)
            return self.found

        self.environment['GCC'] = gcc
        self.environment['GXX'] = gxx
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            website = ('http://gcc.gnu.org',)
            if 'windows' in platform.system().lower():
                if version is None:
                    version = '20120426'
                website = ('http://sourceforge.net/projects/mingw/',
                           'files/Installer/mingw-get-inst/mingw-get-inst-' +
                           str(version) + '/')
            if 'darwin' in platform.system().lower():
                raise Exception('XCode does not appear to be installed.')
            global_install('GCC', website,
                           winstaller='mingw-get-inst-' + str(version) + '.exe',
                           ## brew, port => XCode
                           deb='build-essential g++ autoconf ' + \
                               'automake libtool gettext',
                           rpm='gcc gcc-c++ autoconf automake libtool ' + \
                               'make gettext')
        if not is_installed(environ, version):
            raise Exception('GCC installation failed.')
