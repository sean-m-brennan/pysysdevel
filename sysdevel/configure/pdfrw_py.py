#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find pdfrw
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
pdfrw_found = False


def null():
    pass


def is_installed(environ, version):
    global environment, pdfrw_found
    try:
        import pdfrw
        ver = pdfrw.__version__
        if compare_versions(ver, version) == -1:
            return pdfrw_found
        pdfrw_found = True
    except:
        pass
    return pdfrw_found


def install(environ, version, locally=True):
    if not pdfrw_found:
        website = 'https://pypi.python.org/packages/source/p/pdfrw/'
        if version is None:
            version = '0.1'
        src_dir = 'pdfrw-' + str(version)
        archive = src_dir + '.tar.gz' 
        install_pypkg(src_dir, website, archive, locally=locally)
        if not is_installed(environ, version):
            raise Exception('pdfrw installation failed.')
