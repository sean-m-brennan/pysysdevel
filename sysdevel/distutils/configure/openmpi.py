
import os
import sys
import struct
import subprocess

from ..prerequisites import find_header, find_libraries, find_program, programfiles_directories, autotools_install, global_install, ConfigError
from ..configuration import lib_config
from .. import options

class configuration(lib_config):
    """
    Find/install OpenMPI library
    """
    def __init__(self):
        lib_config.__init__(self, "openmpi", "mpi.h", debug=False)


    def is_installed(self, environ, version=None, strict=False):
        options.set_debug(self.debug)
        openmpi_lib_list = ['mpi', 'mpi_cxx', 'mpi_f90']
        arch = 'i686'
        if struct.calcsize('P') == 8:
            arch = 'x86_64'

        base_dirs = []
        limit = False
        if 'OPENMPI_LIB_DIR' in environ and environ['OPENMPI_LIB_DIR']:
            base_dirs.append(environ['OPENMPI_LIB_DIR'])
            limit = True
            if 'OPENMPI_INCLUDE_DIR' in environ and environ['OPENMPI_INCLUDE_DIR']:
                base_dirs.append(environ['OPENMPI_INCLUDE_DIR'])

        if not limit:
            try:
                base_dirs += os.environ['LD_LIBRARY_PATH'].split(os.pathsep)
                base_dirs += os.environ['CPATH'].split(os.pathsep)
            except KeyError:
                pass
            try:
                base_dirs.append(os.environ['OPENMPI_ROOT'])
            except KeyError:
                pass
            for d in programfiles_directories():
                base_dirs.append(os.path.join(d, 'OPENMPI'))
            try:
                base_dirs.append(environ['MINGW_DIR'])
                base_dirs.append(environ['MSYS_DIR'])
            except KeyError:
                pass

        try:
            subdirs = [os.path.join('openmpi', 'lib')]
            openmpi_lib_dir, openmpi_libs  = find_libraries(openmpi_lib_list[0],
                                                            base_dirs, subdirs)
            openmpi_inc_dir = find_header(self.hdr, base_dirs,
                                          ['openmpi', 'openmpi-' + arch,])
            openmpi_exe = find_program('mpicc', base_dirs +
                                       [os.path.join(openmpi_lib_dir, '..')])
            openmpi_exe_dir = os.path.abspath(os.path.dirname(openmpi_exe))
            self.found = True
        except ConfigError:
            if self.debug:
                print(sys.exc_info()[1])
            return self.found

        os.environ['PATH'] = os.environ.get('PATH', '') + \
                             os.pathsep + openmpi_exe_dir
        self.environment['OPENMPI_PATH'] = openmpi_exe_dir
        self.environment['OPENMPI_INCLUDE_DIR'] = openmpi_inc_dir
        self.environment['OPENMPI_LIB_DIR'] = openmpi_lib_dir
        self.environment['OPENMPI_LIBRARIES'] = openmpi_lib_list
        self.environment['OPENMPI_LIB_FILES'] = openmpi_libs
        try:
            p = subprocess.Popen([openmpi_exe, '-show'],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
            if err != '':
                self.found = False
                return self.found
            self.environment['OPENMPI_FLAGS'] = out.split()[1:]
        except OSError:
            self.found = False
        return self.found


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if version is None:
                version = '1.6.4'
            website = ('http://www.open-mpi.org/',
                       'software/ompi/v' + '.'.join(version.split('.')[:2]) +
                       '/downloads/')
            if locally:
                src_dir = 'openmpi-' + str(version)
                archive = src_dir + '.tar.gz'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('OpenMPI', website,
                               brew='open-mpi', port='openmpi',
                               deb='libopenmpi-dev', rpm='openmpi-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('OPENMPI2 installation failed.')
