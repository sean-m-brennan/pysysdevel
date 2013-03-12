#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find MinGW
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
mingw_found = False


def null():
    global environment
    environment['MSVCRT_DIR'] = None
    environment['MINGW_DIR'] = None
    environment['MINGW_PREFIX'] = '/mingw'
    environment['MSYS_DIR'] = None
    environment['MSYS_SHELL'] = None
    environment['MSYS_PREFIX'] = '/'
    environment['MINGW_CC'] = None
    environment['MINGW_CXX'] = None
    environment['MINGW_FORTRAN'] = None


def is_installed(version=None):
    global environment, mingw_found
    ## Python was (most likely) built with msvcr90.dll, thus it's a dependency
    ## FIXME detect
    environment['MSYS_PREFIX'] = '/'
    environment['MINGW_PREFIX'] = '/mingw'
    try:
        ## the easy/sure way
        environment['MSVCRT_DIR'] = os.environ['MSVCRT_DIR']
    except:
        msvcrt_dirs = [os.path.join(os.environ['ProgramFiles'],
                                    'Microsoft Visual Studio 9.0',
                                    'VC', 'redist', 'x86',
                                    'Microsoft.VC90.CRT'),
                       os.environ['ProgramFiles'],
                       ]
        environment['MSVCRT_DIR'], _ = find_library('msvcr90', msvcrt_dirs)

    try:
        ## the easy way
        mingw_root = os.environ['MINGW_ROOT']
        environment['MINGW_DIR']     = mingw_root
        environment['MSYS_DIR']      = os.path.join(mingw_root, 'msys', '1.0')
        environment['MSYS_SHELL']    = find_program('msys.bat',
                                                    environment['MSYS_DIR'])
        environment['MINGW_CC']      = find_program('mingw32-gcc',
                                             os.path.join(mingw_root, 'bin'))
        environment['MINGW_CXX']     = find_program('mingw32-g++',
                                             os.path.join(mingw_root, 'bin'))
        environment['MINGW_FORTRAN'] = find_program('mingw32-gfortran',
                                             os.path.join(mingw_root, 'bin'))
        mingw_found = True
    except:
        ## look for it
        primary_loc = os.path.join('C:', os.sep, 'MinGW', 'bin')
        try:
            alt_loc = os.path.join(os.environ['ProgramFiles'], 'MinGW', 'bin')
        except:
            alt_loc = None
        environment['MINGW_CC']  = m = find_program('mingw32-gcc',
                                                    [primary_loc, alt_loc,])
        environment['MINGW_CXX']     = find_program('mingw32-g++',
                                                    [primary_loc, alt_loc,])
        environment['MINGW_FORTRAN'] = find_program('mingw32-gfortran',
                                                    [primary_loc, alt_loc,])
        environment['MINGW_DIR']     = os.path.split(m)[0]
        environment['MSYS_DIR']      = os.path.join(os.path.split(m)[0],
                                                    'msys', '1.0')
        environment['MSYS_SHELL']    = find_program('msys.bat',
                                                    environment['MSYS_DIR'])
        mingw_found = True
    return mingw_found


def install(target='build', version=None):
    if not mingw_found:
        if version is None:
            version = '20120426'
        website = ('http://sourceforge.net/projects/mingw/',
                   'files/Installer/mingw-get-inst/mingw-get-inst-' +
                   str(version) + '/')
        global_install('MinGW', website,
                       'mingw-get-inst-' + str(version) + '.exe',
                       'i386-mingw32-binutils i386-mingw32-gcc i386-mingw32-runtime i386-mingw32-w32api',
                       'mingw32-binutils gcc-mingw32 mingw32-runtime',
                       'mingw32-gcc-c++ mingw32-gcc mingw32-pthreads mingw32-w32api mingw32-binutils mingw32-runtime mingw32-filesystem mingw32-cpp mingw32-dlfcn-static')
        is_installed()
