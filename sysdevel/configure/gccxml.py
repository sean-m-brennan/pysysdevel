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
    try:
        base_dirs.append(os.path.join(os.environ['ProgramFiles'],
                                      'GCC_XML', 'bin'))
    except:
        pass
    try:
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
                       _uses_homebrew()):
            here = os.path.abspath(os.getcwd())
            if locally:
                prefix = os.path.abspath(dst_dir)
                if not prefix in local_search_paths:
                    local_search_paths.append(prefix)
            else:
                prefix = global_prefix

            src_dir = 'gccxml'
            os.chdir(download_dir)
            gitsite = 'https://github.com/gccxml/gccxml.git'
            subprocess.check_call([environ['GIT'], 'clone', gitsite, src_dir])
            build_dir = os.path.join(download_dir, src_dir, '_build')
            mkdir(build_dir)
            os.chdir(build_dir)
            config_cmd = [environ['CMAKE'], '..',
                          '-G', '"MSYS Makefiles"',
                          '-DCMAKE_INSTALL_PREFIX=' + prefix,
                          '-DCMAKE_MAKE_PROGRAM=/bin/make.exe']
            if 'windows' in platform.system().lower():
                mingw_check_call(environ, config_cmd)
                mingw_check_call(environ, ['make'])
                mingw_check_call(environ, ['make', 'install'])
            else:
                subprocess.check_call(config_cmd)
                subprocess.check_call(environ, ['make'])
                if locally:
                    subprocess.check_call(environ, ['make', 'install'])
                else:
                    admin_check_call(environ, ['make', 'install'])
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
