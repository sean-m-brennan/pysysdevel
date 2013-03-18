#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find MPICH library
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

import os, struct, glob

from sysdevel.util import *

environment = dict()
mpich_found = False


def null():
    global environment
    environment['MPICH_INCLUDE_DIR'] = None
    environment['MPICH_LIB_DIR'] = None
    environment['MPICH_LIBRARIES'] = []
    environment['MPICH_LIBS'] = []


def is_installed(environ, version):
    global environment, mpich_found
    base_dirs = []
    mpich_lib_list = ['mpich', 'mpichcxx', 'mpichf90']
    if 'windows' in platform.system().lower():
        mpich_lib_list = ['mpi', 'mpicxx', 'fmpich2g']
    arch = 'i686'
    if struct.calcsize('P') == 8:
        arch = 'x86_64'

    try:
        base_dirs.append(os.environ['MPICH_ROOT'])
    except:
        pass
    try:
        base_dirs.append(os.path.join(os.environ['PROGRAMFILES'], 'MPICH2'))
    except:
        pass
    try:
        base_dirs.append(environ['MSYS_DIR'])
    except:
        pass

    try:
        mpich_lib_dir, mpich_libs  = find_libraries(mpich_lib_list[0],
                                                    base_dirs)
        mpich_inc_dir = find_header('mpi.h', base_dirs,
                                    ['mpich2', 'mpich2-' + arch,])
        mpich_found = True
    except Exception,e:
        return mpich_found

    environment['MPICH_INCLUDE_DIR'] = mpich_inc_dir
    environment['MPICH_LIB_DIR'] = mpich_lib_dir
    environment['MPICH_LIBRARIES'] = mpich_libs
    environment['MPICH_LIBS'] = mpich_lib_list
    return mpich_found


def install(environ, version, target='build'):
    if not gsl_found:
        if version is None:
            version = '3.0.2'
        website = ('http://www.mpich.org/',
                   'static/tarballs/' + str(version) + '/')
        if 'windows' in platform.system().lower():
            ## assumes MinGW installed and detected
            here = os.path.abspath(os.getcwd())
            src_dir = 'mpich-' + str(version)
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
            global_install('MPICH', website,
                           None,
                           'mpich-devel',
                           'libmpich2-dev',
                           'mpich2-devel')
        if not is_installed(environ, version):
            raise Exception('MPICH2 installation failed.')
