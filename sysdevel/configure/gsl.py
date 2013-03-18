#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find GNU Scientific Library
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

import os

from sysdevel.util import *

environment = dict()
gsl_found = False


def null():
    global environment
    environment['GSL_INCLUDE_DIR'] = ''
    environment['GSL_LIB_DIR'] = None
    environment['GSL_LIBRARIES'] = []
    environment['GSL_LIBS'] = []


def is_installed(environ, version):
    global environment, gsl_found
    base_dirs = []
    try:
        base_dirs.append(os.environ['GSL_ROOT'])
    except:
        pass
    try:
        base_dirs.append(os.path.join(os.environ['ProgramFiles'], 'GnuWin32'))
    except:
        pass
    try:
        base_dirs.append(environ['MSYS_DIR'])
    except:
        pass
    try:
        inc_dir = find_header('gsl_types.h', base_dirs, ['gsl'])
        lib_dir, libs  = find_libraries('gsl', base_dirs)
        gsl_found = True
    except:
        return gsl_found

    environment['GSL_INCLUDE_DIR'] = inc_dir
    environment['GSL_LIB_DIR'] = lib_dir
    environment['GSL_LIBRARIES'] = libs
    environment['GSL_LIBS'] = ['gsl', 'gslcblas',]
    return gsl_found


def install(environ, version, target='build'):
    if not gsl_found:
        if version is None:
            version = '1.15'
        website = ('ftp://ftp.gnu.org/gnu/gsl/',)
        if 'windows' in platform.system().lower():
            ## assumes MinGW installed and detected
            here = os.path.abspath(os.getcwd())
            src_dir = 'gsl-' + str(version)
            archive = src_dir + '.tar.gz'
            fetch(''.join(website), archive, archive)
            unarchive(os.path.join(here, download_dir, archive),
                      target, src_dir)
            build_dir = os.path.join(src_dir, '_build')
            mkdir(build_dir)
            os.chdir(build_dir)
            mingw_check_call(environ, ['../configure',
                                       '--prefix=' + environ['MSYS_PREFIX']])
            mingw_check_call(environ, ['make'])
            mingw_check_call(environ, ['make', 'install'])
            os.chdir(here)
        else:
            global_install('GSL', website,
                           None,
                           'gsl-devel',
                           'libgsl-dev',
                           'gsl-devel')
        if not is_installed(environ, version):
            raise Exception('GSL installation failed.')
