
import os
import sys
import platform
import subprocess

from sysdevel.distutils.prerequisites import find_header, find_library, find_program, convert2unixpath, check_call, mingw_check_call, admin_check_call, global_install, ConfigError
from sysdevel.distutils.fetching import fetch, unarchive
from sysdevel.distutils.configuration import lib_config
from sysdevel.distutils import options

class configuration(lib_config):
    """
    Find/install NASA Common Data Format library
    """
    def __init__(self):
        lib_config.__init__(self, "cdf", "cdf.h", debug=False)
        if 'windows' in platform.system().lower():
            self.dependencies.append('mingw')


    def is_installed(self, environ, version=None, strict=False):
        options.set_debug(self.debug)
        lib_name = 'cdf'
        if 'windows' in platform.system().lower():
            lib_name += 'NativeLibrary'
        if version is None:
            version = '35_0'

        limit = False
        base_dirs = []
        if 'CDF_BASE' in environ and environ['CDF_BASE']:
            base_dirs.append(environ['CDF_BASE'])
            limit = True
        if 'CDF_LIB' in environ and environ['CDF_LIB']:
            base_dirs.append(environ['CDF_LIB'])
            limit = True
        if 'CDF_INC' in environ and environ['CDF_INC']:
            base_dirs.append(environ['CDF_INC'])
            limit = True
        if 'CDF_BIN' in environ and environ['CDF_BIN']:
            base_dirs.append(environ['CDF_BIN'])
            limit = True
        if 'CDF_LIB_DIR' in environ and environ['CDF_LIB_DIR']:
            base_dirs.append(environ['CDF_LIB_DIR'])
            limit = True
            if 'CDF_INCLUDE_DIR' in environ and environ['CDF_INCLUDE_DIR']:
                base_dirs.append(environ['CDF_INCLUDE_DIR'])

        if not limit:
            try:
                base_dirs += os.environ['LD_LIBRARY_PATH'].split(os.pathsep)
                base_dirs += os.environ['CPATH'].split(os.pathsep)
            except KeyError:
                pass
            if 'windows' in platform.system().lower():
                base_dirs.append(os.path.join('C:', os.sep, 'CDF Distribution',
                                              'cdf' + version + '-dist'))
            try:
                base_dirs.append(environ['MINGW_DIR'])
                base_dirs.append(environ['MSYS_DIR'])
            except KeyError:
                pass
        try:
            incl_dir = find_header(self.hdr, base_dirs, limit=limit)
            lib_dir, lib = find_library(self.lib, base_dirs, limit=limit)
            exe = find_program('cdfcompare',  base_dirs)
            self.found = True
        except ConfigError:
            if self.debug:
                print(sys.exc_info()[1])
            return self.found

        self.environment['CDF_INCLUDE_DIR'] = incl_dir
        self.environment['CDF_LIB_DIR'] = lib_dir
        self.environment['CDF_LIB_FILES'] = [lib]
        self.environment['CDF_LIBRARIES'] = [lib_name]
        os.environ['CDF_LIB'] = os.path.abspath(lib_dir)
        os.environ['CDF_INC'] = os.path.abspath(incl_dir)
        os.environ['CDF_BIN'] = os.path.abspath(os.path.dirname(exe))
        return self.found


    def download(self, environ, version, strict=False):
        if version is None:
            version = '35_0'
        website = 'http://cdaweb.gsfc.nasa.gov/pub/software/cdf/dist/cdf' + \
                  str(version)
        os_dir = 'linux'
        if 'windows' in platform.system().lower():
            os_dir = 'windows/src_distribution'
        elif 'darwin' in platform.system().lower():
            os_dir = 'macosX/src_distribution'

        web_subdir = '/' + os_dir + '/'
        src_dir = 'cdf' + str(version) + '-dist'
        archive = src_dir + '-cdf.tar.gz'
        fetch(website + web_subdir, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if locally or not 'darwin' in platform.system().lower():
                here = os.path.abspath(os.getcwd())
                if locally:
                    prefix = os.path.abspath(options.target_build_dir)
                    if not prefix in options.local_search_paths:
                        options.add_local_search_path(prefix)
                else:
                    prefix = options.global_prefix
                ## MinGW shell strips backslashes
                prefix = convert2unixpath(prefix)
                
                src_dir = self.download(environ, version, strict)
                oper_sys = 'linux'
                if 'windows' in platform.system().lower():
                    oper_sys = 'mingw'
                elif 'darwin' in platform.system().lower():
                    oper_sys = 'macosx'
                build_dir = os.path.join(options.target_build_dir, src_dir)
                os.chdir(build_dir)
                log = open('build.log', 'w')
                if 'windows' in platform.system().lower():
                    try:
                        ## ncurses prerequisite
                        check_call(['mingw-get', 'install', 'pdcurses'])
                        check_call(['mingw-get', 'install', 'libpdcurses'])
                    except subprocess.CalledProcessError:
                        pass
                    mingw_check_call(environ, ['make',
                                               'OS=mingw', 'ENV=gnu', 'all'],
                                     stdout=log, stderr=log)
                    mingw_check_call(environ, ['make',
                                               'INSTALLDIR=' + prefix, 'install'],
                                     stdout=log, stderr=log)
                else:
                    check_call(['make', 'OS=' + oper_sys, 'ENV=gnu', 'all'],
                               stdout=log, stderr=log)
                    if locally:
                        check_call(['make', 'INSTALLDIR=' + prefix, 'install'],
                                   stdout=log, stderr=log)
                    else:
                        admin_check_call(['make', 'INSTALLDIR=' + prefix,
                                          'install'], stdout=log, stderr=log)
                log.close()
                os.chdir(here)
            else:
                global_install('CDF', None, brew='cdf', port='cdf')
            if not self.is_installed(environ, version, strict):
                raise Exception('CDF installation failed.')
