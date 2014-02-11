
import sys

from ..prerequisites import find_library, ConfigError
from ..configuration import lib_config
from .. import options

class configuration(lib_config):
    """
    Find/install GCC OpenMP library
    """
    def __init__(self):
        lib_config.__init__(self, "gomp", None,
                            dependencies=['gcc'], debug=False)


    def null(self):
        self.environment['GOMP_LIBRARY_DIR'] = None
        self.environment['GOMP_LIBRARY'] = ''


    def is_installed(self, environ, version=None, strict=False):
        options.set_debug(self.debug)
        try:
            gomp_lib_dir, gomp_lib  = find_library('gomp')
            self.environment['GOMP_LIBRARY_DIR'] = gomp_lib_dir
            self.environment['GOMP_LIBRARY'] = gomp_lib
            self.found = True
        except ConfigError:
            if self.debug:
                print(sys.exc_info()[1])
        return self.found


    def install(self, environ, version, strict=False, locally=True):
        raise Exception('GOMP is part of GCC; Your development environment ' +
                        'is seriously screwed up. Look for libgomp.so.')
