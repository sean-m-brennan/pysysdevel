#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find liblzf
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
lzf_found = False
DEBUG = False


def null():
    global environment
    environment['LZF_INCLUDE_DIR'] = ''
    environment['LZF_LIBRARY_DIR'] = None
    environment['LZF_LIBRARIES'] = []
    environment['LZF_LIBS'] = []


def is_installed(environ, version):
    global environment, lzf_found
    set_debug(DEBUG)
    base_dirs = []
    try:
        base_dirs.append(environ['MSYS_DIR'])
    except:
        pass
    try:
        inc_dir = find_header('lzf.h', base_dirs, ['lzf'])
        lib_dir, libs  = find_libraries('lzf', base_dirs)
        lzf_found = True
    except Exception, e:
        if DEBUG:
            print e
        return lzf_found

    environment['LZF_INCLUDE_DIR'] = inc_dir
    environment['LZF_LIBRARY_DIR'] = lib_dir
    environment['LZF_LIBRARIES'] = libs
    environment['LZF_LIBS'] = ['lzf']
    return lzf_found


def install(environ, version, target='build', locally=True):
    if not lzf_found:
        if version is None:
            version = '3.6'
        website = ('http://dist.schmorp.de/liblzf/Attic/',)
        if locally or 'windows' in platform.system().lower():
            src_dir = 'liblxf-' + str(version)
            archive = src_dir + '.tar.gz'
            autotools_install(environ, website, archive, src_dir, target, locally)
        else:
            global_install('LZF', website,
                           None,
                           'liblzf',
                           'liblzf-dev',
                           'liblzf-devel')
        if not is_installed(environ, version):
            raise Exception('LZF installation failed.')
