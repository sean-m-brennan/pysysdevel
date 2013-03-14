#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find CMake
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
cmake_found = False


def null():
    global environment
    environment['CMAKE'] = None


def is_installed(environ, version):
    global environment, cmake_found
    if version is None:
        version = '2.8'
    base_dirs = []
    try:
        base_dirs.append(os.path.join(os.environ['ProgramFiles'],
                                      'CMake ' + version, 'bin'))
    except:
        pass
    try:
        base_dirs.append(os.path.join(environ['MSYS_DIR'], 'bin'))
    except:
        pass
    try:
        environment['CMAKE'] = find_program('cmake', base_dirs)
        cmake_found = True
    except:
        pass
    return cmake_found


def install(environ, version, target='build'):
    if not cmake_found:
        if version is None:
            version = '2.8.10.2'
        website = ('http://www.cmake.org/',
                   'files/v' + major_minor_version(version) + '/')
        global_install('CMake', website,
                       'cmake-' + str(version) + '-win32-x86.exe',
                       'cmake',
                       'cmake',
                       'cmake')
        if not is_installed(environ, version):
            raise Exception('CMake installation failed.')
