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

from sysdevel.util import *

environment = dict()
geos_found = False


def null():
    global environment
    environment['GEOS_INCLUDE_DIR'] = None
    environment['GEOS_LIBRARY_DIR'] = None
    environment['GEOS_LIBRARIES'] = []
    environment['GEOS_LIBS'] = []


def is_installed(environ, version):
    global environment, geos_found
    base_dirs = []
    try:
        base_dirs.append(os.environ['GEOS_ROOT'])
    except:
        pass
    if 'windows' in platform.system().lower():
        base_dirs.append(os.path.join('C:', os.sep, 'OSGeo4W'))
        try:
            base_dirs.append(environ['MSYS_DIR'])
        except:
            pass
    try:
        lib_dir, libs  = find_libraries('geos_c', base_dirs)
        inc_dir = find_header('geos_c.h', base_dirs)
        quoted_ver = get_header_version(os.path.join(inc_dir, 'geos_c.h'),
                                        'GEOS_VERSION ')
        ver = quoted_ver[1:-1]
        if compare_versions(ver, version) == -1:
            return geos_found
        geos_found = True
    except:
        return geos_found

    environment['GEOS_INCLUDE_DIR'] = inc_dir
    environment['GEOS_LIBRARY_DIR'] = lib_dir
    environment['GEOS_LIBRARIES'] = libs
    environment['GEOS_LIBS'] = ['geos', ' geos_c',]
    return geos_found


def install(environ, version, target='build', locally=True):
    if not geos_found:
        if version is None:
            version = '3.3.8'
        website = ('http://trac.osgeo.org/geos/',)
        if locally or 'windows' in platform.system().lower():
            website = ('http://download.osgeo.org/geos/',)
            src_dir = 'geos-' + str(version)
            archive = src_dir + '.tar.bz2'
            autotools_install(environ, website, archvie, src_dir, target, locally)
        else:
            global_install('Geos', website,
                           None,
                           'geos',
                           'libgeos-dev',
                           'geos-devel')
        if not is_installed(environ, version):
            raise Exception('Geos installation failed.')
