#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find GEOS library
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
geos_found = False


def null():
    global environment
    environment['GEOS_INCLUDE_DIR'] = None
    environment['GEOS_LIBRARY_DIR'] = None
    environment['GEOS_LIBRARIES'] = []
    environment['GEOS_LIBS'] = []


def is_installed(version=None):
    global environment, geos_found
    geos_dev_dir = ''
    try:
        try:
            geos_dev_dir = os.environ['GEOS_ROOT']
        except:
            pass
        if geos_dev_dir != '':
            geos_lib_dir, geos_libs  = find_libraries('geos_c', [geos_dev_dir])
            geos_inc_dir = find_header('geos_c.h', [geos_dev_dir])
        else:
            base_dirs = []
            if 'windows' in platform.system().lower():
                base_dirs += ['C:\\OSGeo4W']
            geos_lib_dir, geos_libs  = find_libraries('geos_c', base_dirs)
            geos_inc_dir = find_header('geos_c.h', base_dirs)
        quoted_ver = get_header_version(os.path.join(geos_inc_dir, 'geos_c.h'),
                                        'GEOS_VERSION ')
        ver = quoted_ver[1:-1]
        if not version is None and ver < version:
            print 'Found libgeos_c v.' + ver
            return geos_found
        environment['GEOS_INCLUDE_DIR'] = geos_inc_dir
        environment['GEOS_LIBRARY_DIR'] = geos_lib_dir
        environment['GEOS_LIBRARIES'] = geos_libs
        environment['GEOS_LIBS'] = ['geos', ' geos_c',]
        geos_found = True
    except Exception,e:
        print e
        geos_found = False
    return geos_found


def install(target='build', version=None):
    ## User must install
    raise Exception('GEOS development library required, but not installed.' +
                    '\nTry http://trac.osgeo.org/geos/;' +
                    ' or yum install geos-devel')
