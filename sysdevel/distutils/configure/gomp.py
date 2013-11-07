
from ..prerequisites import *
from ..configuration import lib_config

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


    def is_installed(self, environ, version):
        set_debug(self.debug)
        try:
            gomp_lib_dir, gomp_lib  = find_library('gomp')
            self.environment['GOMP_LIBRARY_DIR'] = gomp_lib_dir
            self.environment['GOMP_LIBRARY'] = gomp_lib
            self.found = True
        except Exception as e:
            if self.debug:
                print(e)
        return self.found


    def install(self, environ, version, locally=True):
        raise Exception('GOMP is part of GCC; Your development environment ' +
                        'is seriously screwed up. Look for libgomp.so.')
