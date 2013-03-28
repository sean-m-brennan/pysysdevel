#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find Breathe
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

DEPENDENCIES = ['sphinx']

environment = dict()
breathe_found = False


def null():
    pass


def is_installed(environ, version):
    global environment, breathe_found
    try:
        import breathe
        ver = breathe.__version__
        if compare_versions(ver, version) == -1:
            return breathe_found
        breathe_found = True
    except:
        pass
    return breathe_found


def install(environ, version, locally=True):
    if not breathe_found:
        website = 'https://pypi.python.org/packages/source/b/breathe/'
        if version is None:
            version = '0.7.5'
        src_dir = 'breathe-' + str(version)
        archive = src_dir + '.tar.gz' 
        install_pypkg(src_dir, website, archive, locally=locally)
        if not is_installed(environ, version):
            raise Exception('Breathe installation failed.')
