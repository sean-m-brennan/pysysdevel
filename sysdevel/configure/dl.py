
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
