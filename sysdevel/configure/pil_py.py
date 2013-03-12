#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find/install Python image library
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
pil_found = False


def null():
    pass


def is_installed(version=None):
    global pil_found
    try:
        import PIL.Image
        ver = PIL.Image.VERSION
        if not version is None and ver < version:
            return pil_found
        pil_found = True
    except Exception,e:
        print 'PIL not found: ' + str(e)
    return pil_found


def install(target='build', version=None):
    if not pil_found:
        website = 'http://effbot.org/downloads/'
        if version is None:
            version = '1.1.7'
        archive = 'Imaging-' + version + '.tar.gz'
        install_pypkg_locally('Imaging-' + version, website, archive, target)
