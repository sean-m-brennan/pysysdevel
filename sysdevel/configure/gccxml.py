#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find GCCXML
"""
#**************************************************************************
# 
# This material was prepared by the Los Alamos National Security, LLC 
# (LANS), under Contract DE-AC52-06NA25396 with the U.S. Department of 
# Energy (DOE). All rights in the material are reserved by DOE on behalf 
# of the Government and LANS pursuant to the contract. You are authorized 
# to use the material for Government purposes but it is not to be released 
# or distributed to the public. NEITHER THE UNITED STATES NOR THE UNITED 
# STATES DEPARTMENT OF ENERGY, NOR LOS ALAMOS NATIONAL SECURITY, LLC, NOR 
# ANY OF THEIR EMPLOYEES, MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR 
# ASSUMES ANY LEGAL LIABILITY OR RESPONSIBILITY FOR THE ACCURACY, 
# COMPLETENESS, OR USEFULNESS OF ANY INFORMATION, APPARATUS, PRODUCT, OR 
# PROCESS DISCLOSED, OR REPRESENTS THAT ITS USE WOULD NOT INFRINGE 
# PRIVATELY OWNED RIGHTS.
# 
#**************************************************************************

import os, subprocess

from sysdevel.util import *

environment = dict()
gccxml_found = False
DEBUG = False


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
        if compare_versions(version, '0.6') == 1 and \
                'GIT' in environ.keys() and \
                'CMAKE' in environ.keys() and \
                'windows' in platform.system().lower():
            ## assumes MinGW, git, and cmake are installed and detected
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
            mingw_check_call(environ, [environ['GIT'],
                                       'clone', gitsite, src_dir])
            build_dir = os.path.join(download_dir, src_dir, '_build')
            mkdir(build_dir)
            os.chdir(build_dir)
            mingw_check_call(environ, [environ['CMAKE'], '..',
                                       '-G', '"MSYS Makefiles"',
                                       '-DCMAKE_INSTALL_PREFIX=' + prefix,
                                       '-DCMAKE_MAKE_PROGRAM=/bin/make.exe'])
            mingw_check_call(environ, ['make'])
            mingw_check_call(environ, ['make', 'install'])
            os.chdir(here)
        else:
            ## TODO: No local-only installation
            if version is None:
                version = '0.6.0'
            website = ('http://www.gccxml.org/',
                       'files/v' + major_minor_version(version) + '/')
            global_install('GCCXML', website,
                           'gccxml-' + str(version) + '-win32.exe',
                           'gccxml-devel',
                           'gccxml',
                           'gccxml')
        if not is_installed(environ, version):
            raise Exception('GCC-XML installation failed.')
