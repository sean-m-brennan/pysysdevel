
import os
import sys
import platform

from ..prerequisites import find_header, find_libraries, autotools_install, global_install, ConfigError
from ..configuration import lib_config
from .. import options

class configuration(lib_config):
    """
    Find/install PROJ4 library
    """
    def __init__(self):
        lib_config.__init__(self, "proj", "proj_api.h", debug=False)


    def is_installed(self, environ, version=None, strict=False):
        options.set_debug(self.debug)
        base_dirs = []
        limit = False
        if 'PROJ4_LIB_DIR' in environ and environ['PROJ4_LIB_DIR']:
            base_dirs.append(environ['PROJ4_LIB_DIR'])
            limit = True
            if 'PROJ4_INCLUDE_DIR' in environ and environ['PROJ4_INCLUDE_DIR']:
                base_dirs.append(environ['PROJ4_INCLUDE_DIR'])

        if not limit:
            try:
                base_dirs += os.environ['LD_LIBRARY_PATH'].split(os.pathsep)
            except KeyError:
                pass
            try:
                base_dirs.append(os.environ['PROJ4_ROOT'])
            except KeyError:
                pass
            if 'windows' in platform.system().lower():
                base_dirs.append(os.path.join('C:', os.sep, 'OSGeo4W'))
            try:
                base_dirs.append(environ['MINGW_DIR'])
                base_dirs.append(environ['MSYS_DIR'])
            except KeyError:
                pass
        try:
            proj4_inc_dir = find_header(self.hdr, base_dirs)
            proj4_lib_dir, proj4_libs  = find_libraries(self.lib, base_dirs)
            self.found = True
        except ConfigError:
            if self.debug:
                print(sys.exc_info()[1])
            return self.found

        self.environment['PROJ4_INCLUDE_DIR'] = proj4_inc_dir
        self.environment['PROJ4_LIBRARY_DIR'] = proj4_lib_dir
        self.environment['PROJ4_LIBRARIES'] = ['proj']
        self.environment['PROJ4_LIB_FILES'] = proj4_libs
        return self.found


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if version is None:
                version = '4.8.0'
            website = ('http://trac.osgeo.org/proj/',)
            if locally or 'windows' in platform.system().lower():
                website = ('http://download.osgeo.org/proj/',)
                src_dir = 'proj-' + str(version)
                archive = src_dir + '.tar.gz'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('PROJ4', website,
                               brew='proj', port='libproj4',
                               deb='libproj-dev', rpm='proj-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('Proj4 installation failed.')

