
import os
import platform

from sysdevel.util import *
from sysdevel.configuration import lib_config

class configuration(lib_config):
    """
    Find/install GEOS library
    """
    def __init__(self):
        lib_config.__init__(self, "geos_c", "geos_c.h", debug=False)


    def is_installed(self, environ, version):
        set_debug(self.debug)
        locations = []
        limit = False
        if 'GEOS_LIB_DIR' in environ and environ['GEOS_LIB_DIR']:
             locations.append(environ['GEOS_LIB_DIR'])
             limit = True
             if 'GEOS_INCLUDE_DIR' in environ and environ['GEOS_INCLUDE_DIR']:
                 locations.append(environ['GEOS_INCLUDE_DIR'])

        if not limit:
            try:
                locations += os.environ['LD_LIBRARY_PATH'].split(os.pathsep)
            except:
                pass
            try:
                locations.append(os.environ['GEOS_ROOT'])
            except:
                pass
            if 'windows' in platform.system().lower():
                locations.append(os.path.join('C:', os.sep, 'OSGeo4W'))
            try:
                locations.append(environ['MINGW_DIR'])
                locations.append(environ['MSYS_DIR'])
            except:
                pass
        try:
            lib_dir, libs  = find_libraries(self.lib, locations, limit=limit)
            inc_dir = find_header(self.hdr, locations, limit=limit)
            quoted_ver = get_header_version(os.path.join(inc_dir, self.hdr),
                                            'GEOS_VERSION ')
            ver = quoted_ver[1:-1]
            if compare_versions(ver, version) == -1:
                return self.found
            self.found = True
        except Exception as e:
            if self.debug:
                print(e)
            return self.found

        self.environment['GEOS_INCLUDE_DIR'] = inc_dir
        self.environment['GEOS_LIBRARY_DIR'] = lib_dir
        self.environment['GEOS_LIBRARIES'] = ['geos', ' geos_c',]
        self.environment['GEOS_LIB_FILES'] = libs
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '3.3.8'
            website = ('http://trac.osgeo.org/geos/',)
            if locally or 'windows' in platform.system().lower():
                website = ('http://download.osgeo.org/geos/',)
                src_dir = 'geos-' + str(version)
                archive = src_dir + '.tar.bz2'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('Geos', website,
                               None,
                               brew='geos', port='geos',
                               deb='libgeos-dev', rpm='geos-devel')
            if not self.is_installed(environ, version):
                raise Exception('Geos installation failed.')
