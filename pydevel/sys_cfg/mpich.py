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

from pydevel.util import *

environment = dict()
mpich_found = False


def null():
    global environment
    environment['MPICH_INCLUDE_DIR'] = None
    environment['MPICH_LIBRARY_DIR'] = None
    environment['MPICH_LIBRARIES'] = []
    environment['MPICH_LIBS'] = []


def is_installed(version=None):
    global environment, mpich_found
    mpich_dev_dir = ''
    try:
        arch = 'i686'
        if struct.calcsize('P') == 8:
            arch = 'x86_64'
        try:
            mpich_dev_dir = os.environ['MPICH_ROOT']
        except:
            pass
        if mpich_dev_dir != '':
            mpich_lib_dir, mpich_lib  = find_library('mpich', [mpich_dev_dir])
            mpich_inc_dir = find_header('mpi.h', [mpich_dev_dir],
                                        ['mpich2', 'mpich2-' + arch,])
        else:
            base_dirs = []
            if 'windows' in platform.system().lower():
                base_dirs += [os.path.join('c:', 'mpich')] #FIXME
            mpich_lib_dir, mpich_libs  = find_libraries('mpich', base_dirs)
            mpich_inc_dir = find_header('mpi.h', base_dirs,
                                        ['mpich2', 'mpich2-' + arch,])
        environment['MPICH_INCLUDE_DIR'] = mpich_inc_dir
        environment['MPICH_LIBRARY_DIR'] = mpich_lib_dir
        environment['MPICH_LIBRARIES'] = mpich_libs
        environment['MPICH_LIBS'] = ['mpich', 'mpichcxx', 'mpichf90',]
        ## FIXME derive from found libs
        mpich_found = True
    except Exception,e:
        print e
        mpich_found = False
    return mpich_found


def install(target='build', version=None):
    ## User must install
    raise Exception('MPICH development library required, but not installed.' +
                    '\nTry http://www.mpich.org/downloads/;' +
                    ' or yum install mpich2-devel')
