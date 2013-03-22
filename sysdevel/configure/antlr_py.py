#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find/install Antlr Python runtime
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
antlr_python_found = False


def null():
    pass


def is_installed(environ, version):
    global environment, antlr_python_found
    try:
        import antlr3
        antlr_python_found = True
    except Exception,e:
        pass
    return antlr_python_found


def install(environ, version, target='build'):
    global environment
    if not antlr_python_found:
        website = 'http://www.antlr3.org/download/'
        if version is None:
            version = '3.1.2'
        src_dir = 'antlr_python_runtime-' + str(version)
        archive = src_dir + '.tar.gz' 
        install_pypkg_locally(src_dir, website + 'Python/', archive, target)
        if not is_installed(environ, version):
            raise Exception('ANTLR Python runtime installation failed.')
