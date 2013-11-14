
import os
import platform

from ..prerequisites import *
from ..configuration import config
from .. import options

class configuration(config):
    """
    Find/fetch/install MinGW
    """
    def __init__(self):
        config.__init__(self, debug=False)


    def null(self):
        self.environment['MINGW_DIR'] = None
        self.environment['MSYS_DIR'] = None
        self.environment['MSYS_SHELL'] = None
        self.environment['MINGW_CC'] = None
        self.environment['MINGW_CXX'] = None
        self.environment['MINGW_FORTRAN'] = None


    def is_installed(self, environ, version):
        options.set_debug(self.debug)
        if 'MSVC' in environ:
            raise Exception('MinGW *and* MS Visual C both specified ' +
                            'as the chosen compiler.')
        limit = False
        if 'MINGW_DIR' in environ and environ['MINGW_DIR']:
            mingw_root = environ['MINGW_DIR']
            limit = True

        if not limit:
            try:
                mingw_root = os.environ['MINGW_ROOT']
            except:
                locations = [os.path.join('C:', os.sep, 'MinGW')]
                for d in programfiles_directories():
                    locations.append(os.path.join(d, 'MinGW'))
                try:
                    gcc = find_program('mingw32-gcc', locations)
                    mingw_root = os.path.abspath(os.path.join(
                            os.path.dirname(gcc), '..'))
                except Exception:
                    if self.debug:
                        e = sys.exc_info()[1]
                        print(e)
                    return self.found

        msys_root = os.path.join(mingw_root, 'msys', '1.0')
        try:
            
            gcc = find_program('mingw32-gcc', [mingw_root], limit=limit)
            gxx = find_program('mingw32-g++', [mingw_root], limit=limit)
            gfort = find_program('mingw32-gfortran', [mingw_root], limit=limit)
            self.found = True
        except Exception:
            if self.debug:
                print(sys.exc_info()[1])
            return self.found

        self.environment['MINGW_DIR']     = mingw_root
        self.environment['MSYS_DIR']      = msys_root
        self.environment['MINGW_CC']      = gcc
        self.environment['MINGW_CXX']     = gxx
        self.environment['MINGW_FORTRAN'] = gfort
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            if not 'windows' in platform.system().lower():
                raise Exception('Not installing MinGW on this platform. ' +
                                'Cross compiling not (yet) supported.')
            if version is None:
                version = '20120426'
            website = ('http://sourceforge.net/projects/mingw/',
                       'files/Installer/mingw-get-inst/mingw-get-inst-' +
                       str(version) + '/')
            global_install('MinGW', website,
                           winstaller='mingw-get-inst-' + str(version) + '.exe')
            if not self.is_installed(environ, version):
                raise Exception('MinGW installation failed.')
