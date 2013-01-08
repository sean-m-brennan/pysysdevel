#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find ctypesgen package
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

from pydevel.util import *

environment = dict()
ctypesgen_found = False


def null():
    global environment
    environment['CTYPESGEN_EXE'] = None


def is_installed(version=None):
    global environment, ctypesgen_found
    try:
        environment['CTYPESGEN_EXE'] = find_program('ctypesgen.py')
        ctypesgen_found = True
    except:
        pass
    return ctypesgen_found


def install(target='build', version=None):
    global environment
    if not ctypesgen_found:
        website = 'http://pypi.python.org/packages/source/c/ctypesgen/'
        if version is None:
            version = '0.r125'
        archive = 'ctypesgen-' + version + '.tar.gz'
        install_pypkg_locally('ctypesgen-' + version, website, archive, target)
        environment['CTYPESGEN_EXE'] = \
            find_program('ctypesgen.py', [os.path.join(target, 'bin')])
