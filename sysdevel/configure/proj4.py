
import platform

from sysdevel.util import *
from sysdevel.configuration import lib_config

class configuration(lib_config):
    """
    Find/install PROJ4 library
    """
    def __init__(self):
        lib_config.__init__(self, "proj", "proj_api.h", debug=False)


    def is_installed(self, environ, version):
        set_debug(self.debug)
        base_dirs = []
        limit = False
        if 'PROJ4_LIB_DIR' in environ:
            base_dirs.append(environ['PROJ4_LIB_DIR'])
            limit = True
            if 'PROJ4_INCLUDE_DIR' in environ:
                base_dirs.append(environ['PROJ4_INCLUDE_DIR'])

        if not limit:
            try:
                base_dirs.append(os.environ['PROJ4_ROOT'])
            except:
                pass
            if 'windows' in platform.system().lower():
                base_dirs.append(os.path.join('C:', os.sep, 'OSGeo4W'))
            try:
                base_dirs.append(environ['MINGW_DIR'])
                base_dirs.append(environ['MSYS_DIR'])
            except:
                pass
        try:
            proj4_inc_dir = find_header(self.hdr, base_dirs)
            proj4_lib_dir, proj4_libs  = find_libraries(self.lib, base_dirs)
            self.found = True
        except Exception, e:
            if self.debug:
                print e
            return self.found

        self.environment['PROJ4_INCLUDE_DIR'] = proj4_inc_dir
        self.environment['PROJ4_LIBRARY_DIR'] = proj4_lib_dir
        self.environment['PROJ4_LIBRARIES'] = proj4_libs
        self.environment['PROJ4_LIBS'] = ['proj',]
        return self.found


    def install(self, environ, version, locally=True):
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
            if not self.is_installed(environ, version):
                raise Exception('Proj4 installation failed.')

