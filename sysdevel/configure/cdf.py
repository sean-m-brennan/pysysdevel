
import os
import platform
import subprocess

from sysdevel.util import *
from sysdevel.configuration import lib_config

class configuration(lib_config):
    """
    Find/install NASA Common Data Format library
    """
    def __init__(self):
        lib_config.__init__(self, "cdf", "cdf.h", debug=False)
        if 'windows' in platform.system().lower():
            self.dependencies.append(['mingw'])


    def is_installed(self, environ, version):
        set_debug(self.debug)
        lib_name = 'cdf'
        if 'windows' in platform.system().lower():
            lib_name += 'NativeLibrary'

        limit = False
        base_dirs = []
        if 'CDF_LIB_DIR' in environ and environ['CDF_LIB_DIR']:
            base_dirs.append(environ['CDF_LIB_DIR'])
            limit = True
            if 'CDF_INCLUDE_DIR' in environ and environ['CDF_INCLUDE_DIR']:
                base_dirs.append(environ['CDF_INCLUDE_DIR'])

        if not limit:
            if 'windows' in platform.system().lower():
                base_dirs.append(os.path.join('C:', os.sep, 'CDF Distribution',
                                              'cdf' + version + '-dist'))
            try:
                base_dirs.append(environ['MINGW_DIR'])
                base_dirs.append(environ['MSYS_DIR'])
            except:
                pass
        try:
            incl_dir = find_header(self.hdr, base_dirs, limit=limit)
            lib_dir, lib = find_library(self.lib, base_dirs, limit=limit)
            self.found = True
        except Exception, e:
            if self.debug:
                print e
            return self.found

        self.environment['CDF_INCLUDE_DIR'] = incl_dir
        self.environment['CDF_LIB_DIR'] = lib_dir
        self.environment['CDF_LIB_FILES'] = [lib]
        self.environment['CDF_LIBRARIES'] = [lib_name]
        return self.found


    def install(self, environ, version, locally=True):
        global local_search_paths
        if not self.found:
            if version is None:
                version = '34_1'
            website = ('http://cdf.gsfc.nasa.gov/',)
            if locally or not 'darwin' in platform.system().lower():
                here = os.path.abspath(os.getcwd())
                if locally:
                    prefix = os.path.abspath(target_build_dir)
                    if not prefix in local_search_paths:
                        local_search_paths.append(prefix)
                else:
                    prefix = global_prefix
                ## MinGW shell strips backslashes
                prefix = convert2unixpath(prefix)

                website = ('http://cdaweb.gsfc.nasa.gov/',
                           'pub/software/cdf/dist/cdf' + str(version))
                oper_sys = os_dir = 'linux'
                if 'windows' in platform.system().lower():
                    os_dir = 'windows/src_distribution'
                    oper_sys = 'mingw'
                elif 'darwin' in platform.system().lower():
                    oper_sys = 'macosx'
                    os_dir = 'macosX/src_distribution'

                web_subdir = '/' + os_dir + '/'
                src_dir = 'cdf' + str(version) + '-dist'
                archive = src_dir + '-cdf.tar.gz'
                fetch(''.join(website) + web_subdir, archive, archive)
                unarchive(archive, src_dir)

                build_dir = os.path.join(target_build_dir, src_dir)
                os.chdir(build_dir)
                log = open('build.log', 'w')
                if 'windows' in platform.system().lower():
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
                global_install('CDF', website, brew='cdf', port='cdf')
            if not self.is_installed(environ, version):
                raise Exception('CDF installation failed.')
