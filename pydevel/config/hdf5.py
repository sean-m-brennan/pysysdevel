#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find HDF5 library
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

import os, glob

from pydevel.util import *

environment = dict()
hdf5_found = False


def null():
    global environment
    environment['HDF5_INCLUDE_DIR'] = None
    environment['HDF5_LIBRARY_DIR'] = None
    environment['HDF5_LIBRARIES'] = []
    environment['HDF5_LIBS'] = []


def is_installed():
    global environment, hdf5_found
    hdf5_dev_dir = ''
    try:
        try:
            hdf5_dev_dir = os.environ['HDF5_ROOT']
        except:
            pass
        if hdf5_dev_dir != '':
            hdf5_lib_dir, hdf5_libs  = find_libraries('hdf5', [hdf5_dev_dir])
            hdf5_inc_dir = find_header('hdf5.h', [hdf5_dev_dir])
        else:
            base_dirs = []
            if 'windows' in platform.system().lower():
                base_dirs += [os.path.join('c:', 'hdf5')] #FIXME
            hdf5_lib_dir, hdf5_libs  = find_libraries('hdf5', base_dirs)
            hdf5_inc_dir = find_header('hdf5.h', base_dirs)
        environment['HDF5_INCLUDE_DIR'] = hdf5_inc_dir
        environment['HDF5_LIBRARY_DIR'] = hdf5_lib_dir
        environment['HDF5_LIBRARIES'] = hdf5_libs
        environment['HDF5_LIBS'] = ['hdf5',  'hdf5_fortran', 'hdf5_cpp',
                                    'hdf5_hl', 'hdf5hl_fortran', 'hdf5_hl_cpp',]
        ## FIXME derive from found libs
        hdf5_found = True
    except Exception,e:
        print e
        hdf5_found = False
    return hdf5_found


def install(target='build'):
    ## User must install
    raise Exception('HDF5 development library required, but not installed.' +
                    '\nTry http://www.hdfgroup.org/HDF5/release/obtain5.html;' +
                    ' or yum install hdf5-devel')
