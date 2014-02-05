
import os
import sys
import shutil

from ..prerequisites import find_header, ConfigError
from ..fetching import fetch
from ..configuration import config
from .. import options

class configuration(config):
    """
    Find/install F2C
    """
    def __init__(self):
        config.__init__(self, debug=False)


    def null(self):
        self.environment['F2C_INCLUDE_DIR'] = None


    def is_installed(self, environ, version):
        options.set_debug(self.debug)
        try:
            incl_dir = find_header('f2c.h')
            ## f2c lib is built into libgfortran
            self.found = True
        except ConfigError:
            if self.debug:
                print(sys.exc_info()[1])
            return self.found
        self.environment['F2C_INCLUDE_DIR'] = incl_dir
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            website = 'http://www.netlib.org/f2c/'
            header_file = 'f2c.h'        
            fetch(''.join(website), header_file, header_file)
            shutil.copy(os.path.join(options.download_dir, header_file),
                        options.target_build_dir)
            self.environment['F2C_INCLUDE_DIR'] = options.target_build_dir
            prefix = os.path.abspath(options.target_build_dir)
            if not prefix in options.local_search_paths:
                options.add_local_search_path(prefix)
