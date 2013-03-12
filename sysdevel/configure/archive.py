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

from sysdevel.util import *

environment = dict()
archive_found = False


def null():
    global environment
    environment['ARCHIVE_INCLUDE_DIR'] = None
    environment['ARCHIVE_LIB_DIR'] = None
    environment['ARCHIVE_LIBS'] = []
    environment['ARCHIVE_LIBRARIES'] = []


def is_installed(environ, version):
    global environment, archive_found
    locations = []
    try:
        locations.append(os.environ['ARCHIVE_ROOT'])
    except:
        pass
    try:
        locations.append(os.path.join(os.environ['ProgramFiles'], 'GnuWin32'))
    except:
        pass
    try:
        locations.append(environ['MSYS_DIR'])
    except:
        pass
    try:
        incl_dir = find_header('archive.h', locations)
        lib_dir, lib = find_library('archive', locations)
        archive_found = True
    except:
        return archive_found

    environment['ARCHIVE_INCLUDE_DIR'] = incl_dir
    environment['ARCHIVE_LIB_DIR'] = lib_dir
    environment['ARCHIVE_LIBS'] = [lib]
    environment['ARCHIVE_LIBRARIES'] = ['archive']
    return archive_found


def install(environ, version, target='build'):
    if not archive_found:
        if version is None:
            version = '3.1.2'
        website = ('http://libarchive.org/',
                   'downloads/')
        if 'windows' in platform.system().lower():
            ## assumes MinGW installed and detected
            here = os.path.abspath(os.getcwd())
            src_dir = 'libarchive-' + str(version)
            archive = src_dir + '.tar.gz'
            fetch(''.join(website), archive, archive)
            unarchive(os.path.join(here, download_dir, archive),
                      target, src_dir)
            build_dir = os.path.join(src_dir, '_build')
            mkdir(build_dir)
            os.chdir(build_dir)
            mingw_check_call(environ, ['../configure',
                                       '--prefix=' + environ['MSYS_PREFIX']])
            mingw_check_call(environ, ['make'])
            mingw_check_call(environ, ['make', 'install'])
            os.chdir(here)
        else:
            global_install('Archive', website,
                           None,
                           'libarchive',
                           'libarchive-dev',
                           'libarchive-devel')
        is_installed()
