#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find GNU Scientific Library
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
gsl_found = False


def null():
    global environment
    environment['GSL_INCLUDE_DIR'] = None
    environment['GSL_LIBRARY_DIR'] = None
    environment['GSL_LIBRARIES'] = []
    environment['GSL_LIBS'] = []


def is_installed(version=None):
    global environment, gsl_found
    gsl_dev_dir = ''
    try:
        try:
            gsl_dev_dir = os.environ['GSL_ROOT']
        except:
            pass
        if gsl_dev_dir != '':
            gsl_lib_dir, gsl_libs  = find_libraries('gsl', [gsl_dev_dir])
            gsl_inc_dir = find_header('gsl_types.h', [gsl_dev_dir], ['gsl'])
        else:
            base_dirs = []
            if 'windows' in platform.system().lower():
                base_dirs += [os.path.join('c:', 'gsl')] #FIXME
            gsl_lib_dir, gsl_libs  = find_libraries('gsl', base_dirs)
            gsl_inc_dir = find_header('gsl_types.h', base_dirs, ['gsl'])
        environment['GSL_INCLUDE_DIR'] = gsl_inc_dir
        environment['GSL_LIBRARY_DIR'] = gsl_lib_dir
        environment['GSL_LIBRARIES'] = gsl_libs
        environment['GSL_LIBS'] = ['gsl', 'gslcblas',]
        gsl_found = True
    except Exception,e:
        print e
        gsl_found = False
    return gsl_found


def install(target='build', version=None):
    ## User must install
    raise Exception('GSL development library required, but not installed.' +
                    '\nTry ftp://ftp.gnu.org/gnu/gsl/gsl-1.15.tar.gz;' +
                    ' or yum install gsl-devel')
