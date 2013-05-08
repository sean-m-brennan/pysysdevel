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
import platform

from sysdevel.util import *

environment = dict()
archive_found = False
DEBUG = False


def null():
    global environment
    environment['ARCHIVE_INCLUDE_DIR'] = None
    environment['ARCHIVE_LIB_DIR'] = None
    environment['ARCHIVE_LIBS'] = []
    environment['ARCHIVE_LIBRARIES'] = []


def is_installed(environ, version):
    global environment, archive_found
    set_debug(DEBUG)
    locations = []
    try:
        locations.append(os.environ['ARCHIVE_ROOT'])
    except:
        pass
    for d in programfiles_directories():
        locations.append(os.path.join(d, 'GnuWin32'))
    try:
        locations.append(environ['MINGW_DIR'])
        locations.append(environ['MSYS_DIR'])
    except:
        pass
    try:
        incl_dir = find_header('archive.h', locations)
        lib_dir, lib = find_library('archive', locations)
        archive_found = True
    except Exception, e:
        if DEBUG:
            print e
        return archive_found

    environment['ARCHIVE_INCLUDE_DIR'] = incl_dir
    environment['ARCHIVE_LIB_DIR'] = lib_dir
    environment['ARCHIVE_LIBS'] = [lib]
    environment['ARCHIVE_LIBRARIES'] = ['archive']
    return archive_found


def install(environ, version, locally=True):
    if not archive_found:
        if version is None:
            version = '3.1.2'
        website = ('http://libarchive.org/',
                   'downloads/')
        if locally or 'windows' in platform.system().lower():
            src_dir = 'libarchive-' + str(version)
            archive = src_dir + '.tar.gz'
            autotools_install(environ, website, archive, src_dir, locally)
        else:
            global_install('Archive', website,
                           brew='libarchive', port='libarchive',
                           deb='libarchive-dev', rpm='libarchive-devel')
        if not is_installed(environ, version):
            raise Exception('libarchive installation failed.')
