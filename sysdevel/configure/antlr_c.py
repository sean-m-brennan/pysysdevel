#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find/install Antlr C runtime
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

import platform, shutil, os
from sysdevel.util import *


environment = dict()
antlr_c_found = False
DEBUG = False


def null():
    global environment
    environment['ANTLR_C_INCLUDE_DIR'] = ''
    environment['ANTLR_C_LIB_DIR'] = None
    environment['ANTLR_C_LIBRARIES'] = []
    environment['ANTLR_C_LIBS'] = []


def is_installed(environ, version):
    global environment, antlr_c_found
    set_debug(DEBUG)
    try:
        base_dirs.append(environ['MSYS_DIR'])
    except:
        pass
    try:
        inc_dir = find_header('antlr3.h', base_dirs)
        lib_dir, libs  = find_libraries('antlr3c', base_dirs)
        antlr_c_found = True
    except Exception, e:
        if DEBUG:
            print e
        return antlr_c_found

    environment['ANTLR_C_INCLUDE_DIR'] = inc_dir
    environment['ANTLR_C_LIB_DIR'] = lib_dir
    environment['ANTLR_C_LIBRARIES'] = libs
    environment['ANTLR_C_LIBS'] = ['antlr3c']
    return antlr_c_found


def install(environ, version, target='build', locally=True):
    global environment
    if not antlr_c_found:
        website = 'http://www.antlr3.org/download/'
        if version is None:
            version = '3.1.2'
        src_dir = 'libantlr3c-' + str(version)
        archive = src_dir + '.tar.gz'
        autotools_install(environ, website, archive, src_dir, target, locally)
        if not is_installed(environ, version):
            raise Exception('ANTLR-C runtime installation failed.')
