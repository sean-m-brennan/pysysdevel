#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find PROJ4 library
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
proj4_found = False


def null():
    global environment
    environment['PROJ4_INCLUDE_DIR'] = None
    environment['PROJ4_LIBRARY_DIR'] = None
    environment['PROJ4_LIBRARIES'] = []
    environment['PROJ4_LIBS'] = []


def is_installed(version=None):
    global environment, proj4_found
    proj4_dev_dir = ''
    try:
        try:
            proj4_dev_dir = os.environ['PROJ4_ROOT']
        except:
            pass
        if proj4_dev_dir != '':
            proj4_lib_dir, proj4_libs  = find_libraries('proj', [proj4_dev_dir])
            proj4_inc_dir = find_header('proj_api.h', [proj4_dev_dir])
        else:
            base_dirs = []
            if 'windows' in platform.system().lower():
                base_dirs += [os.path.join('C:', os.sep, 'OSGeo4W')]
            proj4_lib_dir, proj4_libs  = find_libraries('proj', base_dirs)
            proj4_inc_dir = find_header('proj_api.h', base_dirs)
        environment['PROJ4_INCLUDE_DIR'] = proj4_inc_dir
        environment['PROJ4_LIBRARY_DIR'] = proj4_lib_dir
        environment['PROJ4_LIBRARIES'] = proj4_libs
        environment['PROJ4_LIBS'] = ['proj',]
        ## FIXME derive from found libs
        proj4_found = True
    except Exception,e:
        print e
        proj4_found = False
    return proj4_found


def install(target='build', version=None):
    ## User must install
    raise Exception('PROJ4 development library required, but not installed.' +
                    '\nTry http://trac.osgeo.org/proj/;' +
                    ' or yum install proj-devel')
