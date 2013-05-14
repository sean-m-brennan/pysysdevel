
import os
import platform

from sysdevel.util import *
from sysdevel.configuration import lib_config

class configuration(lib_config):
    """
    Find/install HDF5 library
    """
    def __init__(self):
        lib_config.__init__(self, "hdf5", "hdf5.h", debug=False)


    def is_installed(self, environ, version):
        set_debug(self.debug)
        base_dirs = []
        limit = False
        if 'HDF5_LIB_DIR' in environ:
            base_dirs.append(environ['HDF5_LIB_DIR'])
            limit = True
            if 'HDF5_INCLUDE_DIR' in environ:
                base_dirs.append(environ['HDF5_INCLUDE_DIR'])

        if not limit:
            try:
                base_dirs.append(os.environ['HDF5_ROOT'])
            except:
                pass
            for d in programfiles_directories():
                base_dirs.append(os.path.join(d, 'HDF_Group', 'HDF5'))
            try:
                base_dirs.append(environ['MINGW_DIR'])
                base_dirs.append(environ['MSYS_DIR'])
            except:
                pass
        try:
            hdf5_lib_dir, hdf5_libs  = find_libraries(self.lib, base_dirs,
                                                      limit=limit)
            hdf5_inc_dir = find_header(slef.hdr, base_dirs, limit=limit)
            self.found = True
        except Exception, e:
            if self.debug:
                print e
            return self.found

        hdf5_lib_list = ['hdf5', 'hdf5_fortran', 'hdf5_cpp',
                         'hdf5_hl', 'hdf5hl_fortran', 'hdf5_hl_cpp',]
        if 'windows' in platform.system().lower():
            hdf5_lib_list = ['hdf5dll', 'hdf5_fortrandll', 'hdf5_cppdll',
                             'hdf5_hldll', 'hdf5_hl_fortrandll', 'hdf5_hl_cppdll',]
        self.environment['HDF5_INCLUDE_DIR'] = hdf5_inc_dir
        self.environment['HDF5_LIB_DIR'] = hdf5_lib_dir
        self.environment['HDF5_LIBS'] = hdf5_lib_list
        self.environment['HDF5_LIBRARIES'] = hdf5_libs
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '1.8.10'
            website = ('http://www.hdfgroup.org/',
                       'ftp/HDF5/releases/hdf5-1.8.10/src-' +
                       str(version) + '/')
            if locally or 'windows' in platform.system().lower():
                src_dir = 'hdf5-' + str(version)
                archive = src_dir + '.tar.bz2'
                autotools_install(environ, website, archive, src_dir, locally,
                                  extra_cfg=['--enable-cxx', '--enable-fortran'])
            else:
                global_install('HDF5', website,
                               brew='hdf5', port='hdf5',
                               deb='hdf5-devel', rpm='libhdf5-dev')
            if not self.is_installed(environ, version):
                raise Exception('HDF5 installation failed.')
