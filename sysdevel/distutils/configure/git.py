
import os
import sys
import platform

from sysdevel.distutils.prerequisites import programfiles_directories, find_program, global_install, ConfigError
from sysdevel.distutils.configuration import prog_config
from sysdevel.distutils import options

class configuration(prog_config):
    """
    Find/install Git
    """
    def __init__(self):
        prog_config.__init__(self, 'git', debug=False)


    def is_installed(self, environ, version=None, strict=False):
        options.set_debug(self.debug)
        base_dirs = []
        if 'GIT' in environ and environ['GIT']:
            base_dirs.append(os.path.dirname(environ['GIT']))

        base_dirs.append(os.path.join('C:',  os.sep, 'msysgit', 'cmd'))
        for d in programfiles_directories():
            base_dirs.append(os.path.join(d, 'Git', 'cmd'))
        try:
            base_dirs.append(environ['MINGW_DIR'])
            base_dirs.append(environ['MSYS_DIR'])
        except KeyError:
            pass
        try:
            self.environment['GIT'] = find_program('git', base_dirs)
            self.found = True
        except ConfigError:
            if self.debug:
                print(sys.exc_info()[1])
        return self.found


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            website = ('http://git-scm.com/',)
            if 'windows' in platform.system().lower():
                if version is None:
                    version = '1.8.1.2-preview21130201'
                website = ('http://msysgit.googlecode.com/', 'files/')
            #TODO no local install
            global_install('Git', website,
                           winstaller='Git-' + str(version) + '.exe',
                           brew='git', port='git-core',
                           deb='git', rpm='git')
            if not self.is_installed(environ, version, strict):
                raise Exception('Git installation failed.')
