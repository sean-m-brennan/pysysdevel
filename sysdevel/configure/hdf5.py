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

from sysdevel.util import *

environment = dict()
hdf5_found = False
DEBUG = False


def null():
    global environment
    environment['HDF5_INCLUDE_DIR'] = None
    environment['HDF5_LIB_DIR'] = None
    environment['HDF5_LIBRARIES'] = []
    environment['HDF5_LIBS'] = []


def is_installed(environ, version):
    global environment, hdf5_found
    set_debug(DEBUG)
    base_dirs = []
    try:
        base_dirs.append(os.environ['HDF5_ROOT'])
    except:
        pass
    if 'windows' in platform.system().lower():
        try:
            progfiles = os.environ['ProgramFiles']
            base_dirs.append(os.path.join(progfiles, 'HDF_Group', 'HDF5'))
        except:
            pass
        try:
            base_dirs.append(environ['MSYS_DIR'])
        except:
            pass
    try:
        hdf5_lib_dir, hdf5_libs  = find_libraries('hdf5', base_dirs)
        hdf5_inc_dir = find_header('hdf5.h', base_dirs)
        hdf5_found = True
    except Exception, e:
        if DEBUG:
            print e
        return hdf5_found

    hdf5_lib_list = ['hdf5', 'hdf5_fortran', 'hdf5_cpp',
                     'hdf5_hl', 'hdf5hl_fortran', 'hdf5_hl_cpp',]
    if 'windows' in platform.system().lower():
        hdf5_lib_list = ['hdf5dll', 'hdf5_fortrandll', 'hdf5_cppdll',
                         'hdf5_hldll', 'hdf5_hl_fortrandll', 'hdf5_hl_cppdll',]
    environment['HDF5_INCLUDE_DIR'] = hdf5_inc_dir
    environment['HDF5_LIB_DIR'] = hdf5_lib_dir
    environment['HDF5_LIBS'] = hdf5_lib_list
    environment['HDF5_LIBRARIES'] = hdf5_libs
    return hdf5_found


def install(environ, version, target='build', locally=True):
    if not hdf5_found:
        if version is None:
            version = '1.8.10'
        website = ('http://www.hdfgroup.org/',
                   'ftp/HDF5/releases/hdf5-1.8.10/src-' + str(version) + '/')
        if locally or 'windows' in platform.system().lower():
            src_dir = 'hdf5-' + str(version)
            archive = src_dir + '.tar.bz2'
            autotools_install(environ, website, archive, src_dir, target, locally)
        else:
            global_install('HDF5', website,
                           None,
                           'hdf5',
                           'hdf5-devel',
                           'libhdf5-dev')
        if not is_installed(environ, version):
            raise Exception('HDF5 installation failed.')
