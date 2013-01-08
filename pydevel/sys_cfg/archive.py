#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find libarchive
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
archive_found = False


def null():
    global environment
    environment['ARCHIVE_INCLUDE_DIR'] = None
    environment['ARCHIVE_LIB_DIR'] = None


def is_installed(version=None):
    global environment, archive_found
    try:
        ## the easy way
        archive_root = os.environ['ARCHIVE_ROOT']
        environment['ARCHIVE_INCLUDE_DIR'] = os.path.join(archive_root,
                                                          'include')
        environment['ARCHIVE_LIB_DIR'] = os.path.join(archive_root, 'lib')
        archive_found = True
    except:
        ## look for it
        try:
            win_loc = os.path.join(os.environ['ProgramFiles'], 'GnuWin32')
        except:
            win_loc = None
        incl_dir = find_header('archive.h', [win_loc,])
        environment['ARCHIVE_INCLUDE_DIR'] = incl_dir
        environment['ARCHIVE_LIB_DIR'], _ = find_library('archive',
                                                         [win_loc,])
        archive_found = True
    return archive_found


def install(target='build', version=None):
    if not archive_found:
        raise Exception('Archive not found. (ARCHIVE_ROOT=' +
                        str(environment['ARCHIVE_ROOT']) + ', include=' +
                        str(environment['ARCHIVE_INCLUDE_DIR']) + ', library=' +
                        str(environment['ARCHIVE_LIB_DIR']) + ')')
