
import os
import sys
import platform

from ..prerequisites import find_header, find_libraries, compare_versions, autotools_install_without_fetch, global_install, ConfigError
from ..headers import get_header_version
from ..fetching import fetch, unarchive
from ..configuration import lib_config
from .. import options

class configuration(lib_config):
    """
    Find/install GEOS library
    """
    def __init__(self):
        lib_config.__init__(self, "geos_c", "geos_c.h", debug=False)


    def is_installed(self, environ, version=None, strict=False):
        options.set_debug(self.debug)
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
            except KeyError:
                pass
            try:
                locations.append(os.environ['GEOS_ROOT'])
            except KeyError:
                pass
            if 'windows' in platform.system().lower():
                locations.append(os.path.join('C:', os.sep, 'OSGeo4W'))
            try:
                locations.append(environ['MINGW_DIR'])
                locations.append(environ['MSYS_DIR'])
            except KeyError:
                pass
        try:
            lib_dir, libs  = find_libraries(self.lib, locations, limit=limit)
            inc_dir = find_header(self.hdr, locations, limit=limit)
            quoted_ver = get_header_version(os.path.join(inc_dir, self.hdr),
                                            'GEOS_VERSION ')
            ver = quoted_ver[1:-1]
            not_ok = (compare_versions(ver, version) == -1)
            if strict:
                not_ok = (compare_versions(ver, version) != 0)
            if not_ok:
                if self.debug:
                    print('Wrong version of ' + self.lib + ': ' +
                          str(ver) + ' vs ' + str(version))
                return self.found
            self.found = True
        except ConfigError:
            if self.debug:
                e = sys.exc_info()[1]
                print(e)
            return self.found

        self.environment['GEOS_INCLUDE_DIR'] = inc_dir
        self.environment['GEOS_LIBRARY_DIR'] = lib_dir
        self.environment['GEOS_LIBRARIES'] = ['geos', ' geos_c',]
        self.environment['GEOS_LIB_FILES'] = libs
        return self.found


    def download(self, environ, version, strict=False):
        if version is None:
            version = '3.3.8'
        website = 'http://download.osgeo.org/geos/'
        src_dir = 'geos-' + str(version)
        archive = src_dir + '.tar.bz2'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if locally or 'windows' in platform.system().lower():
                src_dir = self.download(environ, version, strict)
                autotools_install_without_fetch(environ, src_dir, locally)
            else:
                global_install('Geos', None,
                               brew='geos', port='geos',
                               deb='libgeos-dev', rpm='geos-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('Geos installation failed.')
