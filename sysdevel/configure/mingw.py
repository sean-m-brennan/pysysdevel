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
    environment['MINGW_CC'] = None
    environment['MINGW_FORTRAN'] = None
    environment['MINGW_CXX'] = None


def is_installed(version=None):
    global environment, mingw_found
    ## Python was (most likely) built with msvcr90.dll, thus it's a dependency
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
        environment['MINGW_CC']      = find_program('mingw32-gcc.exe',
                                             os.path.join(mingw_root, 'bin'))
        environment['MINGW_FORTRAN'] = find_program('mingw32-gfortran.exe',
                                             os.path.join(mingw_root, 'bin'))
        environment['MINGW_CXX']     = find_program('mingw32-g++.exe',
                                             os.path.join(mingw_root, 'bin'))
        mingw_found = True
    except:
        ## look for it
        primary_loc = os.path.join('C:', os.sep, 'MinGW', 'bin')
        try:
            alt_loc = os.path.join(os.environ['ProgramFiles'], 'MinGW', 'bin')
        except:
            alt_loc = None
        environment['MINGW_CC']      = find_program('mingw32-gcc.exe',
                                                    [primary_loc, alt_loc,])
        environment['MINGW_FORTRAN'] = find_program('mingw32-gfortran.exe',
                                                    [primary_loc, alt_loc,])
        environment['MINGW_CXX'] = m = find_program('mingw32-g++.exe',
                                                    [primary_loc, alt_loc,])
        environment['MINGW_DIR']     = os.path.split(m)[0]
        mingw_found = True
    return mingw_found


def install(target='build', version=None):
    if not mingw_found:
        raise Exception('MinGW required, but not found.')
