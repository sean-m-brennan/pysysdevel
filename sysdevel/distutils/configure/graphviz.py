
import os
import sys
import platform

from ..prerequisites import programfiles_directories, find_header, find_library, autotools_install_without_fetch, global_install, ConfigError
from ..fetching import fetch, unarchive
from ..filesystem import glob_insensitive
from ..configuration import lib_config
from .. import options

class configuration(lib_config):
    """
    Find/install Graphviz library
    """
    def __init__(self):
        lib_config.__init__(self, "cgraph", "cgraph.h",
                            dependencies=[], #TODO lots of dependencies
                            debug=False)


    def null(self):
        self.environment['GRAPHVIZ_INCLUDE_DIR'] = None
        self.environment['GRAPHVIZ_LIB_DIR'] = None
        self.environment['GRAPHVIZ_SHLIB_DIR'] = None
        self.environment['GRAPHVIZ_LIB_FILES'] = None
        self.environment['GRAPHVIZ_LIBRARIES'] = None


    def is_installed(self, environ, version=None, strict=False):
        options.set_debug(self.debug)
        base_dirs = []
        limit = False
        if 'GRAPHVIZ_LIB_DIR' in environ and \
                environ['GRAPHVIZ_LIB_DIR']:
            base_dirs.append(environ['GRAPHVIZ_LIB_DIR'])
            limit = True
            if 'GRAPHVIZ_INCLUDE_DIR' in environ and \
                    environ['GRAPHVIZ_INCLUDE_DIR']:
                base_dirs.append(environ['GRAPHVIZ_INCLUDE_DIR'])

        if not limit:
            try:
                base_dirs += os.environ['LD_LIBRARY_PATH'].split(os.pathsep)
                base_dirs += os.environ['CPATH'].split(os.pathsep)
            except KeyError:
                pass
            try:
                base_dirs.append(os.environ['GRAPHVIZ_ROOT'])
            except KeyError:
                pass
            for d in programfiles_directories():
                base_dirs.append(os.path.join(d, 'GnuWin32'))
                base_dirs += glob_insensitive(d, self.lib + '*')
            try:
                base_dirs.append(environ['MINGW_DIR'])
                base_dirs.append(environ['MSYS_DIR'])
            except KeyError:
                pass
        try:
            incl_dir = find_header(self.hdr, base_dirs, limit=limit)
            lib_dir, lib = find_library(self.lib, base_dirs, limit=limit)
            self.found = True
        except ConfigError:
            if self.debug:
                e = sys.exc_info()[1]
                print(e)
            return self.found

        self.environment['GRAPHVIZ_INCLUDE_DIR'] = incl_dir
        self.environment['GRAPHVIZ_LIB_DIR'] = lib_dir
        self.environment['GRAPHVIZ_SHLIB_DIR'] = lib_dir
        self.environment['GRAPHVIZ_LIB_FILES'] = [lib]
        self.environment['GRAPHVIZ_LIBRARIES'] = [self.lib]
        return self.found


    def download(self, environ, version, strict=False):
        if version is None:
            version = '2.30.1'
        website = 'http://www.graphviz.org/pub/graphviz/stable/SOURCES/'
        src_dir = 'graphviz-' + str(version)
        archive = src_dir + '.tar.gz'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if locally or 'windows' in platform.system().lower():
                src_dir = self.download(environ, version, strict)
                autotools_install_without_fetch(environ, src_dir, locally)
            else:
                global_install('Graphviz', None,
                               brew='graphviz', port='graphviz-devel',
                               deb='graphviz-dev', rpm='graphviz-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('Graphviz installation failed.')
