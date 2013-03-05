#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find GCC OpenMP library
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
gomp_found = False


def null():
    global environment
    environment['GOMP_LIBRARY_DIR'] = None
    environment['GOMP_LIBRARY'] = ''


def is_installed(version=None):
    global environment, gomp_found
    try:
        gomp_lib_dir, gomp_lib  = find_library('gomp')
        environment['GOMP_LIBRARY_DIR'] = gomp_lib_dir
        environment['GOMP_LIBRARY'] = gomp_lib
        gomp_found = True
    except Exception,e:
        print e
        gomp_found = False
    return gomp_found


def install(target='build', version=None):
    ## User must install
    raise Exception('GOMP development library required, but not installed.' +
                    '\nlibgomp is part of GCC, your development environment ' +
                    'may be messed up. Try yum install libgomp, at a minimum.')
