
import os
import sys
import struct

from ..prerequisites import find_program, global_install, ConfigError
from ..configuration import prog_config
from .. import options

class configuration(prog_config):
    """
    Find/install Node.js
    """
    def __init__(self):
        prog_config.__init__(self, 'node', debug=False)


    def null(self):
        prog_config.null(self)
        self.environment['NPM'] = None


    def is_installed(self, environ, version=None, strict=False):
        options.set_debug(self.debug)
        prev = prog_config.is_installed(self, environ, version, strict)
        if prev:
            locations = [os.path.dirname(self.environment[self.exe.upper()])]
            try:
                program = find_program('npm', locations, limit=True)
                self.environment['NPM'] = program
            except ConfigError:
                if self.debug:
                    print(sys.exc_info()[1])
                return False
        return prev
        

    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if version is None:
                version = '0.10.15'
            website = ('http://nodejs.org/', 'dist/v' + version +'/')
            arch = 'x86'
            if struct.calcsize('P') == 8:
                arch = 'x64'
                website = (website[0], website[1] + arch + '/')
            #TODO no local install
            global_install('Node.js', website,
                           winstaller='node-v' + version + '-' + arch + 'msi',
                           brew='node, npm', port='nodejs, npm',
                           deb='nodejs, npm', rpm='nodejs, npm')
            if not self.is_installed(environ, version, strict):
                raise Exception('Node.js installation failed.')
