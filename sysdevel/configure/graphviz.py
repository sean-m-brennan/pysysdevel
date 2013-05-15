
import platform

from sysdevel.util import *
from sysdevel.configuration import lib_config

class configuration(lib_config):
    """
    Find/install Graphviz library
    """
    def __init__(self):
        lib_config.__init__(self, "cgraph", "cgraph.h",
                            dependencies=[], #FIXME lots of dependencies
                            debug=False)


    def null(self):
        self.environment['GRAPHVIZ_INCLUDE_DIR'] = None
        self.environment['GRAPHVIZ_LIB_DIR'] = None
        self.environment['GRAPHVIZ_SHLIB_DIR'] = None
        self.environment['GRAPHVIZ_LIB_FILES'] = None
        self.environment['GRAPHVIZ_LIBRARIES'] = None


    def is_installed(self, environ, version=None):
        set_debug(self.debug)

        locations = []
        limit = False
        if 'GRAPHVIZ_LIB_DIR' in environ and \
                environ['GRAPHVIZ_LIB_DIR']:
            locations.append(environ['GRAPHVIZ_LIB_DIR'])
            limit = True
            if 'GRAPHVIZ_INCLUDE_DIR' in environ and \
                    environ['GRAPHVIZ_INCLUDE_DIR']:
                locations.append(environ['GRAPHVIZ_INCLUDE_DIR'])

        if not limit:
            try:
                locations.append(os.environ['GRAPHVIZ_ROOT'])
            except:
                pass
            for d in programfiles_directories():
                locations.append(os.path.join(d, 'GnuWin32'))
                locations += glob_insensitive(d, self.lib + '*')
            try:
                locations.append(environ['MINGW_DIR'])
                locations.append(environ['MSYS_DIR'])
            except:
                pass
        try:
            incl_dir = find_header(self.hdr, locations, limit=limit)
            lib_dir, lib = find_library(self.lib, locations, limit=limit)
            self.found = True
        except Exception, e:
            if self.debug:
                print e
            return self.found

        self.environment['GRAPHVIZ_INCLUDE_DIR'] = incl_dir
        self.environment['GRAPHVIZ_LIB_DIR'] = lib_dir
        #self.environment['GRAPHVIZ_SHLIB_DIR'] = lib_dir #FIXME
        self.environment['GRAPHVIZ_LIB_FILES'] = [lib]
        self.environment['GRAPHVIZ_LIBRARIES'] = [self.lib]
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '2.30.1'
            website = ('http://www.graphviz.org/',
                       'pub/graphviz/stable/SOURCES/')
            if locally or 'windows' in platform.system().lower():
                src_dir = 'graphviz-' + str(version)
                archive = src_dir + '.tar.gz'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('Graphviz', website,
                               brew='graphviz', port='graphviz-devel',
                               deb='graphviz-dev', rpm='graphviz-devel')
            if not self.is_installed(environ, version):
                raise Exception('Graphviz installation failed.')
