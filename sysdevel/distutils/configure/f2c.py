
from ..prerequisites import *
from ..configuration import config

class configuration(config):
    """
    Find/install F2C
    """
    def __init__(self):
        config.__init__(self, debug=False)


    def null(self):
        self.environment['F2C_INCLUDE_DIR'] = None


    def is_installed(self, environ, version):
        set_debug(self.debug)
        try:
            incl_dir = find_header('f2c.h')
            ## f2c lib is built into libgfortran
            self.found = True
        except Exception:
            if self.debug:
                e = sys.exc_info()[1]
                print(e)
            return self.found
        self.environment['F2C_INCLUDE_DIR'] = incl_dir
        return self.found


    def install(self, environ, version, locally=True):
        global local_search_paths
        if not self.found:
            website = 'http://www.netlib.org/f2c/'
            header_file = 'f2c.h'        
            fetch(''.join(website), header_file, header_file)
            shutil.copy(os.path.join(download_dir, header_file),
                        target_build_dir)
            self.environment['F2C_INCLUDE_DIR'] = target_build_dir
            prefix = os.path.abspath(target_build_dir)
            if not prefix in local_search_paths:
                local_search_paths.append(prefix)
