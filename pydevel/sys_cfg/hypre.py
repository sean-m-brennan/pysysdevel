#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find HYPRE library
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

from pydevel.util import *

environment = dict()
hypre_found = False


def null():
    global environment
    environment['HYPRE_INCLUDE_DIR'] = None
    environment['HYPRE_LIBRARY_DIR'] = None
    environment['HYPRE_LIBRARIES'] = []


def is_installed(version=None):
    global environment, hypre_found
    hypre_dev_dir = ''
    try:
        try:
            hypre_dev_dir = os.environ['HYPRE_ROOT']
        except:
            pass
        if hypre_dev_dir != '':
            hypre_lib_dir, hypre_lib  = find_library('hypre', [hypre_dev_dir])
            hypre_inc_dir = find_header('hypre.h', [hypre_dev_dir])
        else:
            base_dirs = []
            if 'windows' in platform.system().lower():
                base_dirs += [os.path.join('c:', 'hypre')] #FIXME
            hypre_lib_dir, hypre_libs  = find_libraries('hypre', base_dirs)
            hypre_inc_dir = find_header('hypre.h', base_dirs)
        environment['HYPRE_INCLUDE_DIR'] = hypre_inc_dir
        environment['HYPRE_LIBRARY_DIR'] = hypre_lib_dir
        environment['HYPRE_LIBRARIES'] = hypre_libs
        hypre_found = True
    except Exception,e:
        print e
        hypre_found = False
    return hypre_found


def install(target='build', version=None):
    ## User must install
    raise Exception('HYPRE development library required, but not installed.' +
                    '\nTry https://computation.llnl.gov/casc/hypre/software.html')
