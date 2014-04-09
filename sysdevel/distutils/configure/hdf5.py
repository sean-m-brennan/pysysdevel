
import os
import sys
import platform
import subprocess

from ..prerequisites import programfiles_directories, find_header, find_libraries, check_call, autotools_install_without_fetch, global_install, ConfigError, compare_versions
from ..fetching import fetch, unarchive
from ..configuration import lib_config
from .. import options

class configuration(lib_config):
    """
    Find/install HDF5 library
    """
    def __init__(self):
        lib_config.__init__(self, "hdf5", "hdf5.h", debug=False)


    def is_installed(self, environ, version=None, strict=False):
        options.set_debug(self.debug)
        base_dirs = []
        limit = False
        if 'HDF5_LIB_DIR' in environ and environ['HDF5_LIB_DIR']:
            base_dirs.append(environ['HDF5_LIB_DIR'])
            limit = True
            if 'HDF5_INCLUDE_DIR' in environ and environ['HDF5_INCLUDE_DIR']:
                base_dirs.append(environ['HDF5_INCLUDE_DIR'])

        if not limit:
            try:
                base_dirs += os.environ['LD_LIBRARY_PATH'].split(os.pathsep)
                base_dirs += os.environ['CPATH'].split(os.pathsep)
            except KeyError:
                pass
            try:
                base_dirs.append(os.environ['HDF5_ROOT'])
            except KeyError:
                pass
            for d in programfiles_directories():
                base_dirs.append(os.path.join(d, 'HDF_Group', 'HDF5'))
            try:
                base_dirs.append(environ['MINGW_DIR'])
                base_dirs.append(environ['MSYS_DIR'])
            except KeyError:
                pass
        try:
            hdf5_lib_dir, hdf5_libs  = find_libraries(self.lib, base_dirs,
                                                      limit=limit)
            hdf5_inc_dir = find_header(self.hdr, base_dirs, limit=limit)

            h = open(os.path.join(hdf5_inc_dir, 'H5public.h'), 'r')
            ver = None
            for line in h.readlines():
                if 'H5_VERS_INFO' in line:
                    pre = 'HDF5 library version: '
                    v_begin = line.find(pre) + len(pre)
                    v_end = line.find('"', v_begin)
                    ver = line[v_begin:v_end].strip()
                    break
            h.close()
            not_ok = (compare_versions(ver, version) == -1)
            if strict:
                not_ok = (compare_versions(ver, version) != 0)
            if not_ok:
                if self.debug:
                    print('Wrong version of ' + self.lib + ': ' +
                          str(ver) + ' vs ' + str(version))
                self.found = False
                return self.found
            self.found = True
        except ConfigError:
            if self.debug:
                print(sys.exc_info()[1])
            return self.found

        hdf5_lib_list = ['hdf5', 'hdf5_fortran', 'hdf5_cpp',
                         'hdf5_hl', 'hdf5hl_fortran', 'hdf5_hl_cpp',]
        if 'windows' in platform.system().lower():
            hdf5_lib_list = ['hdf5dll', 'hdf5_fortrandll', 'hdf5_cppdll',
                             'hdf5_hldll', 'hdf5_hl_fortrandll', 'hdf5_hl_cppdll',]
        self.environment['HDF5_INCLUDE_DIR'] = hdf5_inc_dir
        self.environment['HDF5_LIB_DIR'] = hdf5_lib_dir
        self.environment['HDF5_LIB_FILES'] = hdf5_libs
        self.environment['HDF5_LIBRARIES'] = hdf5_lib_list
        return self.found


    def download(self, environ, version, strict=False):
        if version is None:
            version = '1.8.10'
        website = 'http://www.hdfgroup.org/ftp/HDF5/releases/hdf5-' + \
                  str(version) + '/src/'
        src_dir = 'hdf5-' + str(version)
        archive = src_dir + '.tar.gz'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            env = dict()
            if 'windows' in platform.system().lower():
                env['LIBS'] = '-lws2_32'
                try:
                    ## zlib prerequisite
                    check_call(['mingw-get', 'install', 'libz-dev'])
                except subprocess.CalledProcessError:
                    pass
            if locally or 'windows' in platform.system().lower():
                src_dir = self.download(environ, version, strict)
                autotools_install_without_fetch(environ, src_dir, locally,
                                  extra_cfg=['--enable-cxx','--enable-fortran'],
                                  addtnl_env=env)
            else:
                global_install('HDF5', None,
                               brew='hdf5', port='hdf5',
                               deb='libhdf5-dev', rpm='hdf5-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('HDF5 installation failed.')


    #TODO windows mingw build needs patch
    #TODO Remove h5perf_serial from perform/Makefile.in
