"""
Find GCCXML
"""

import os
import subprocess
import platform

from sysdevel.util import *

environment = dict()
gccxml_found = False
DEBUG = False

DEPENDENCIES = ['git', 'cmake']


def null():
    global environment
    environment['GCCXML'] = None


def is_installed(environ, version):
    global environment, gccxml_found
    set_debug(DEBUG)
    base_dirs = []
    for d in programfiles_directories():
        base_dirs.append(os.path.join(d, 'GCC_XML'))
    try:
        base_dirs.append(environ['MINGW_DIR'])
        base_dirs.append(environ['MSYS_DIR'])
    except:
        pass
    try:
        environment['GCCXML'] = find_program('gccxml', base_dirs)
        gccxml_found = True
    except Exception, e:
        if DEBUG:
            print e
    return gccxml_found


def install(environ, version, locally=True):
    global local_search_paths
    if not gccxml_found:
        if locally or ('darwin' in platform.system().lower() and
                       system_uses_homebrew()):
            here = os.path.abspath(os.getcwd())
            if locally:
                prefix = os.path.abspath(target_build_dir)
                if not prefix in local_search_paths:
                    local_search_paths.append(prefix)
            else:
                prefix = global_prefix
            prefix = convert2unixpath(prefix)  ## MinGW shell strips backslashes

            src_dir = 'gccxml'
            if not os.path.exists(os.path.join(here, download_dir, src_dir)):
                os.chdir(download_dir)
                gitsite = 'https://github.com/gccxml/gccxml.git'
                check_call([environ['GIT'], 'clone', gitsite, src_dir])
                os.chdir(here)
            build_dir = os.path.join(download_dir, src_dir, '_build')
            mkdir(build_dir)
            os.chdir(build_dir)
            log = open('build.log', 'w')
            if 'windows' in platform.system().lower():
                if 'MSVC' in environ:
                    config_cmd = [environ['CMAKE'], '..',
                                  '-G', '"NMake Makefiles"',
                                  '-DCMAKE_INSTALL_PREFIX=' + prefix]
                    check_call([environ['MSVC_VARS']], stdout=log, stderr=log)
                    check_call(config_cmd, stdout=log, stderr=log)
                    check_call([environ['NMAKE']], stdout=log, stderr=log)
                    check_call([environ['NMAKE'], 'install'],
                               stdout=log, stderr=log)
                else:  ## MinGW
                    config_cmd = [environ['CMAKE'], '..',
                                  '-G', '"MSYS Makefiles"',
                                  '-DCMAKE_INSTALL_PREFIX=' + prefix,
                                  '-DCMAKE_MAKE_PROGRAM=/bin/make.exe']
                    mingw_check_call(environ, config_cmd,
                                     stdout=log, stderr=log)
                    mingw_check_call(environ, ['make'], stdout=log, stderr=log)
                    mingw_check_call(environ, ['make', 'install'],
                                 stdout=log, stderr=log)
            else:
                config_cmd = [environ['CMAKE'], '..',
                              '-G', 'Unix Makefiles',
                              '-DCMAKE_INSTALL_PREFIX=' + prefix]
                check_call(config_cmd, stdout=log, stderr=log)
                check_call(['make'], stdout=log, stderr=log)
                if locally:
                    check_call(['make', 'install'], stdout=log, stderr=log)
                else:
                    admin_check_call(['make', 'install'],
                                     stdout=log, stderr=log)
            log.close()
            os.chdir(here)
        else:
            if version is None:
                version = '0.6.0'
            website = ('http://www.gccxml.org/',
                       'files/v' + major_minor_version(version) + '/')
            global_install('GCCXML', website,
                           winstaller='gccxml-' + str(version) + '-win32.exe',
                           brew=None, port='gccxml-devel',
                           deb='gccxml', rpm='gccxml')
        if not is_installed(environ, version):
            raise Exception('GCC-XML installation failed.')
