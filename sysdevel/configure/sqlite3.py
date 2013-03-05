#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find SQLite3
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
sqlite_found = False


def null():
    global environment
    environment['SQLITE3_INCLUDE_DIR'] = None
    environment['SQLITE3_LIB_DIR'] = None
    environment['SQLITE3_LIBRARY'] = None


def is_installed(version=None):
    global environment, sqlite_found
    ## look for it
    try:
        win_loc = os.path.join(os.environ['ProgramFiles'], 'SQLite3')
    except:
        win_loc = None
    incl_dir = find_header('sqlite3.h', [win_loc,])
    environment['SQLITE3_INCLUDE_DIR'] = incl_dir
    environment['SQLITE3_LIB_DIR'], lib = find_library('sqlite3', [win_loc,])
    environment['SQLITE3_LIBRARY'] = 'sqlite3'
    sqlite_found = True
    return sqlite_found


def install(target='build', version=None):
    if not sqlite_found:
        raise Exception('SQLite3 not found. (include=' +
                        str(environment['SQLITE3_INCLUDE_DIR']) + ', library=' +
                        str(environment['SQLITE3_LIB_DIR']) + ')')
