
import os
import platform

from sysdevel.util import *
from sysdevel.configuration import lib_config

class configuration(lib_config):
    """
    Find/install libdl
    """
    def __init__(self):
        lib_config.__init__(self, "dl", "dlfcn.h", debug=False)
        if 'windows' in platform.system().lower():
            self.dependencies.append(['mingw'])


    def is_installed(self, environ, version=None):
        set_debug(self.debug)

        locations = []
        limit = False
        if 'DL_LIB_DIR' in environ:
            locations.append(environ['DL_LIB_DIR'])
            limit = True
            if 'DL_INCLUDE_DIR' in environ:
                locations.append(environ['DL_INCLUDE_DIR'])

        if not limit:
            try:
                locations.append(environ['MINGW_DIR'])
                locations.append(environ['MSYS_DIR'])
            except:
                pass
        try:
            incl_dir = find_header(self.hdr, locations, limit=limit)
            lib_dir, lib = find_library(self.lib, locations,
                                        limit=limit, wildcard=False)
            self.found = True
        except Exception, e:
            if self.debug:
                print e
            return self.found

        self.environment['DL_INCLUDE_DIR'] = incl_dir
        self.environment['DL_LIB_DIR'] = lib_dir
         #self.environment['DL_SHLIB_DIR'] = lib_dir #FIXME
        self.environment['DL_LIB'] = [lib]
        self.environment['DL_LIBRARIES'] = [self.lib]
        return self.found


    def install(self, environ, version, locally=True):
        global local_search_paths
        if not self.found:
            if 'windows' in platform.system().lower():
                here = os.path.abspath(os.getcwd())
                if locally:
                    prefix = os.path.abspath(target_build_dir)
                    if not prefix in local_search_paths:
                        local_search_paths.append(prefix)
                else:
                    prefix = global_prefix
                ## MinGW shell strips backslashes
                prefix = convert2unixpath(prefix)

                website = ('http://dlfcn-win32.googlecode.com/files/',)
                if version is None:
                    version = 'r19'
                src_dir = 'dlfcn-win32-' + str(version)
                archive = src_dir + '.tar.bz2'
                fetch(''.join(website), archive, archive)
                unarchive(archive, src_dir)

                build_dir = os.path.join(target_build_dir, src_dir)
                os.chdir(build_dir)
                log = open('build.log', 'w')
                patch_c_only_header('dlfcn.h')
                mingw_check_call(environ, ['./configure', '--prefix=' + prefix,
                                           '--libdir=' + prefix + '/lib',
                                           '--incdir=' + prefix + '/include',
                                           '--enable-shared'],
                                 stdout=log, stderr=log)
                mingw_check_call(environ, ['make'], stdout=log, stderr=log)
                mingw_check_call(environ, ['make', 'install'],
                                 stdout=log, stderr=log)
                log.close()
                os.chdir(here)
            else:
                raise Exception('Non-Windows platform with missing libdl.')
            if not self.is_installed(environ, version):
                raise Exception('libdl installation failed.')
