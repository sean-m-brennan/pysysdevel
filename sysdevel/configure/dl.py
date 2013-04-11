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

from sysdevel.util import *

environment = dict()
libdl_found = False
DEBUG = False


def null():
    global environment
    environment['DL_INCLUDE_DIR'] = None
    environment['DL_LIB_DIR'] = None
    environment['DL_LIBS'] = None
    environment['DL_LIBRARIES'] = None


def is_installed(environ, version):
    global environment, libdl_found

    set_debug(DEBUG)
    locations = []
    try:
        locations.append(os.environ['MINGW_DIR'])
        locations.append(os.environ['MSYS_DIR'])
    except:
        pass
    try:
        incl_dir = find_header('dlfcn.h', locations)
        lib_dir, lib = find_library('dl', locations)
        libdl_found = True
    except Exception, e:
        if DEBUG:
            print e
        return libdl_found

    environment['DL_INCLUDE_DIR'] = incl_dir
    environment['DL_LIB_DIR'] = lib_dir
    environment['DL_LIB'] = [lib]
    environment['DL_LIBRARIES'] = ['dl']
    return libdl_found


def install(environ, version, locally=True):
    if not libdl_found:
        if 'windows' in platform.system().lower():
            here = os.path.abspath(os.getcwd())
            if locally:
                prefix = os.path.abspath(target_build_dir)
                if not prefix in local_search_paths:
                    local_search_paths.append(prefix)
            else:
                prefix = global_prefix
            prefix = convert2unixpath(prefix)  ## MinGW shell strips backslashes

            website = ('http://dlfcn-win32.googlecode.com/files/',)
            if version is None:
                version = 'r19'
            src_dir = 'dlfcn-win32-' + str(version)
            archive = src_dir + '.tar.bz2'
            fetch(''.join(website), archive, archive)
            unarchive(archive, src_dir)

            build_dir = os.path.join(target_build_dir, src_dir)
            os.chdir(build_dir)
            try:
                mingw_check_call(environ, ['./configure', '--prefix=' + prefix,
                                           '--enable-shared'])
            except:
                pass
            mingw_check_call(environ, ['make'])
            mingw_check_call(environ, ['make', 'install'])
        else:
            raise Exception('Non-Windows platform with missing libdl.')
        if not is_installed(environ, version):
            raise Exception('libdl installation failed.')
