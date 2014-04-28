
import os
import sys
import struct
import platform
import subprocess

from sysdevel.distutils.prerequisites import programfiles_directories, find_libraries, find_header, find_program, autotools_install_without_fetch, global_install, ConfigError
from sysdevel.distutils.fetching import fetch, unarchive
from sysdevel.distutils.configuration import lib_config
from sysdevel.distutils import options

class configuration(lib_config):
    """
    Find/install MPICH library
    """
    def __init__(self):
        lib_config.__init__(self, "mpich2", "mpi.h", debug=False)


    def is_installed(self, environ, version=None, strict=False):
        options.set_debug(self.debug)
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
            except KeyError:
                pass
            try:
                base_dirs.append(os.environ['MPICH_ROOT'])
            except KeyError:
                pass
            for d in programfiles_directories():
                base_dirs.append(os.path.join(d, 'MPICH2'))
            try:
                base_dirs.append(environ['MINGW_DIR'])
                base_dirs.append(environ['MSYS_DIR'])
            except KeyError:
                pass

        try:
            mpich_lib_dir, mpich_libs  = find_libraries(mpich_lib_list[0],
                                                        base_dirs)
            mpich_inc_dir = find_header(self.hdr, base_dirs,
                                        ['mpich2', 'mpich2-' + arch,])
            mpich_exe = find_program('mpicc', base_dirs +
                                     [os.path.join(mpich_lib_dir, '..')])
            mpich_exe_dir = os.path.abspath(os.path.dirname(mpich_exe))
            self.found = True
        except ConfigError:
            if self.debug:
                print(sys.exc_info()[1])
            return self.found

        os.environ['PATH'] = os.environ.get('PATH', '') + \
                             os.pathsep + mpich_exe_dir
        self.environment['MPICH_PATH'] = mpich_exe_dir
        self.environment['MPICH_INCLUDE_DIR'] = mpich_inc_dir
        self.environment['MPICH_LIB_DIR'] = mpich_lib_dir
        self.environment['MPICH_LIBRARIES'] = mpich_lib_list
        self.environment['MPICH_LIB_FILES'] = mpich_libs
        try:
            p = subprocess.Popen([mpich_exe, '-compile_info', '-link_info'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            if err != '':
                self.found = False
                return self.found
            self.environment['MPICH_FLAGS'] = out.split()[1:]
        except OSError:
            self.found = False
        return self.found


    def download(self, environ, version, strict=False):
        if version is None:
            version = '3.0.2'
        website = 'http://www.mpich.org/static/tarballs/' + str(version) + '/'
        src_dir = 'mpich-' + str(version)
        archive = src_dir + '.tar.gz'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            src_dir = self.download(environ, version, strict)
            if locally:
                autotools_install_without_fetch(environ, src_dir, locally)
            else:
                global_install('MPICH', None,
                               brew='mpich2', port='mpich-devel',
                               deb='libmpich2-dev', rpm='mpich2-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('MPICH2 installation failed.')
