#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find/install Python serial package
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
pyserial_found = False


def null():
    pass


def is_installed(environ, version):
    global pyserial_found
    try:
        import serial
        ver = serial.VERSION
        if compare_versions(ver, version) == -1:
            return pyserial_found
        pyserial_found = True
    except:
        pass
    return pyserial_found


def install(environ, version, target='build'):
    global environment
    if not pyserial_found:
        website = 'http://pypi.python.org/packages/source/p/pyserial/'
        if version is None:
            version = '2.6'
        src_dir = 'pyserial-' + version
        archive = src_dir + '.tar.gz'
        install_pypkg_locally(src_dir, website, archive, target)
        if not is_installed(environ, version):
            raise Exception('pyserial installation failed.')
