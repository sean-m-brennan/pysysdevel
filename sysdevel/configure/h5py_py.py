#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find/install H5py (HDF5 for python)
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

from sysdevel.util import *

environment = dict()
h5py_found = False

DEPENDENCIES = [('hdf5', '1.8.3'), 'lzf']

def null():
    pass


def is_installed(environ, version):
    global h5py_found
    try:
        import h5py
        ver = h5py.version.version
        if compare_versions(ver, version) == -1:
            return h5py_found
        h5py_found = True
    except:
        pass
    return h5py_found


def install(environ, version, locally=True):
    if not h5py_found:
        website = 'http://h5py.googlecode.com/files/'
        if version is None:
            version = '2.1.2'
        src_dir = 'h5py-' + str(version)
        archive = src_dir + '.tar.gz'
        install_pypkg(src_dir, website, archive, locally=locally)
        if not is_installed(environ, version):
            raise Exception('h5py installation failed.')
