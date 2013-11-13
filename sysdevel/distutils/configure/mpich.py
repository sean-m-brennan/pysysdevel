
import struct
import platform

from ..prerequisites import *
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install MPICH library
    """
    def __init__(self):
        lib_config.__init__(self, "mpich2", "mpi.h", debug=False)


    def is_installed(self, environ, version):
        set_debug(self.debug)
        mpich_lib_list = ['mpich', 'mpichcxx', 'mpichf90']
        if 'windows' in platform.system().lower():
            mpich_lib_list = ['mpi', 'mpicxx', 'fmpich2g']
        arch = 'i686'
        if struct.calcsize('P') == 8:
            arch = 'x86_64'

        base_dirs = []
        limit = False
        if 'MPICH_LIB_DIR' in environ and environ['MPICH_LIB_DIR']:
            base_dirs.append(environ['MPICH_LIB_DIR'])
            limit = True
            if 'MPICH_INCLUDE_DIR' in environ and environ['MPICH_INCLUDE_DIR']:
                base_dirs.append(environ['MPICH_INCLUDE_DIR'])

        if not limit:
            try:
                base_dirs += os.environ['LD_LIBRARY_PATH'].split(os.pathsep)
                base_dirs += os.environ['CPATH'].split(os.pathsep)
            except:
                pass
            try:
                base_dirs.append(os.environ['MPICH_ROOT'])
            except:
                pass
            for d in programfiles_directories():
                base_dirs.append(os.path.join(d, 'MPICH2'))
            try:
                base_dirs.append(environ['MINGW_DIR'])
                base_dirs.append(environ['MSYS_DIR'])
            except:
                pass

        try:
            mpich_lib_dir, mpich_libs  = find_libraries(mpich_lib_list[0],
                                                        base_dirs)
            mpich_inc_dir = find_header(self.hdr, base_dirs,
                                        ['mpich2', 'mpich2-' + arch,])
            self.found = True
        except Exception:
            if self.debug:
                e = sys.exc_info()[1]
                print(e)
            return self.found

        self.environment['MPICH_INCLUDE_DIR'] = mpich_inc_dir
        self.environment['MPICH_LIB_DIR'] = mpich_lib_dir
        self.environment['MPICH_LIBRARIES'] = mpich_lib_list
        self.environment['MPICH_LIB_FILES'] = mpich_libs
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '3.0.2'
            website = ('http://www.mpich.org/',
                       'static/tarballs/' + str(version) + '/')
            if locally:
                src_dir = 'mpich-' + str(version)
                archive = src_dir + '.tar.gz'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('MPICH', website,
                               brew='mpich2', port='mpich-devel',
                               deb='libmpich2-dev', rpm='mpich2-devel')
            if not self.is_installed(environ, version):
                raise Exception('MPICH2 installation failed.')
