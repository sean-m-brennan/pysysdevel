#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find Uuid
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
uuid_found = False


def null():
    pass


def is_installed(environ, version):
    global environment, uuid_found
    try:
        import uuid
        ver = uuid.__version__
        if compare_versions(ver, version) == -1:
            return uuid_found
        uuid_found = True
    except:
        pass
    return uuid_found


def install(environ, version, locally=True):
    if not uuid_found:
        website = 'https://pypi.python.org/packages/source/u/uuid/'
        if version is None:
            version = '1.30'
        src_dir = 'uuid-' + str(version)
        archive = src_dir + '.tar.gz' 
        install_pypkg(src_dir, website, archive, locally=locally)
        if not is_installed(environ, version):
            raise Exception('Uuid installation failed.')
