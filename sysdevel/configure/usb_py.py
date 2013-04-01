#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find/install Python USB package
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
pyusb_found = False

DEPENDENCIES = ['libusb']

def null():
    pass


def is_installed(environ, version):
    global pyusb_found
    try:
        import usb
        #ver = usb.VERSION
        #if compare_versions(ver, version) == -1:
        #    return pyusb_found
        pyusb_found = True
    except:
        pass
    return pyusb_found


def install(environ, version, locally=True):
    global environment
    if not pyusb_found:
        website = 'http://pypi.python.org/packages/source/p/pyusb/'
        if version is None:
            version = '1.0.0a3'
        src_dir = 'pyusb-' + version
        archive = src_dir + '.tar.gz'
        install_pypkg(src_dir, website, archive, locally=locally)
        if not is_installed(environ, version):
            raise Exception('pyusb installation failed.')
