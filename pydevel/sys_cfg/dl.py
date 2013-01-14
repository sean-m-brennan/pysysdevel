#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find libdl
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
dl_found = False


def null():
    global environment
    environment['DL_INCLUDE_DIR'] = None
    environment['DL_LIB_DIR'] = None


def is_installed(version=None):
    global environment, dl_found
    try:
        extra_loc = os.environ['DL_ROOT']
    except:
        extra_loc = None
    environment['DL_INCLUDE_DIR'] = find_header('dlfcn.h', [extra_loc,])
    environment['DL_LIB_DIR'], _ = find_library('dl', [extra_loc,])
    dl_found = True
    return dl_found


def install(target='build', version=None):
    if not dl_found:
        raise Exception('libdl not found. (DL_ROOT=' +
                        str(environment['DL_ROOT']) + ', include=' +
                        str(environment['DL_INCLUDE_DIR']) + ', library=' +
                        str(environment['DL_LIB_DIR']) + ')')
