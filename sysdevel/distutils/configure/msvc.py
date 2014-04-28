
import os
import sys

from sysdevel.distutils.prerequisites import find_program, programfiles_directories, get_msvc_version, ConfigError
from sysdevel.distutils.configuration import config
from sysdevel.distutils import options

class configuration(config):
    """
    Find MS Visual Studio
    """
    def __init__(self):
        config.__init__(self, debug=False)


    def null(self):
        self.environment['MSVC'] = None
        self.environment['NMAKE'] = None
        self.environment['MSVC_VARS'] = None


    def is_installed(self, environ, version, strict=False):
        options.set_debug(self.debug)
        if 'MINGW_CC' in environ:
            raise Exception('MS Visual C *and* MinGW both specified ' +
                            'as the chosen compiler.')

        version, _, _ = get_msvc_version()
        dot_ver = '.'.join(version)

        vcvars = None
        nmake = None
        msvc = None

        msvc_dirs = []
        limit = False
        if 'MSVC' in environ and environ['MSVC']:
            msvc_dirs.append(os.path.dirname(environ['MSVC']))
            limit = True

        if not limit:
            for d in programfiles_directories():
                msvc_dirs.append(os.path.join(d,
                                              'Microsoft Visual Studio ' + dot_ver,
                                              'VC'))
        try:
            vcvars = find_program('vcvarsall', msvc_dirs, limit=limit)
            nmake = find_program('nmake', msvc_dirs, limit=limit)
            msvc = find_program('cl', msvc_dirs, limit=limit)
            self.found = True
        except ConfigError:
            if self.debug:
                print(sys.exc_info()[1])
            return self.found

        self.environment['MSVC_VARS'] = vcvars
        self.environment['NMAKE'] = nmake
        self.environment['MSVC'] = msvc
        return self.found


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            raise Exception('Install MS Visual Studio by hand')
