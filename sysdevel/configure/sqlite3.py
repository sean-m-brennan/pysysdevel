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
    environment['SQLITE3_LIBS'] = []
    environment['SQLITE3_LIBRARIES'] = []


def is_installed(environ, version):
    global environment, sqlite_found
    locations = []
    try:
        locations.append(environ['MSYS_DIR'])
    except:
        pass
    try:
        incl_dir = find_header('sqlite3.h', locations)
        lib_dir, lib = find_library('sqlite3', locations)
        sqlite_found = True
    except:
        return sqlite_found

    environment['SQLITE3_INCLUDE_DIR'] = incl_dir
    environment['SQLITE3_LIB_DIR'] = lib_dir
    environment['SQLITE3_LIBS'] = [lib]
    environment['SQLITE3_LIBRARIES'] = ['sqlite3']
    return sqlite_found


def install(environ, version, target='build', locally=True):
    if not sqlite_found:
        if version is None:
            version = '3071502'
        website = ('http://sqlite.org/', )
        if locally or 'windows' in platform.system().lower():
            src_dir = 'sqlite-autoconf-' + str(version)
            archive = src_dir + '.tar.gz'
            autotools_install(environ, website, archive, src_dir, target, locally)
        else:
            global_install('SQLite3', website,
                           None,
                           'sqlite3',
                           'libsqlite-dev',
                           'sqlite-devel')
        if not is_installed(environ, version):
            raise Exception('SQLite3 installation failed.')
