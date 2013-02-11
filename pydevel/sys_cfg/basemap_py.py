#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find/install Matplotlib Basemap toolkit
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

import os, platform, glob
from pydevel.util import *

## NB: Basemap documentation lies! It requires Python version > 2.4

environment = dict()
basemap_found = False

geos_min = '3.1.1'
geos_found = False

basemap_data_pathlist = ['mpl-data', 'basemap-data']
basemap_data_dir = os.path.join(*basemap_data_pathlist)


def null():
    global environment
    environment['BASEMAP_VERSION'] = None
    environment['BASEMAP_DATA_PATHLIST'] = []
    environment['BASEMAP_DIR'] = ''
    environment['BASEMAP_DATA_FILES'] = []
    environment['BASEMAP_DEPENDENCIES'] = []


def is_installed(version=None):
    global environment, basemap_found, geos_found
    try:
        from mpl_toolkits import basemap
        ver = basemap.__version__
        if not version is None and ver < version:
            print 'Found basemap v.' + ver
            return basemap_found
        environment['BASEMAP_VERSION'] = version
        environment['BASEMAP_DATA_PATHLIST'] = basemap_data_pathlist
        basemap_dir = os.path.dirname(basemap.__file__)
        environment['BASEMAP_DIR'] = basemap_dir
        environment['BASEMAP_DATA_FILES'] = \
            [(basemap_data_dir,
              glob.glob(os.path.join(basemap_dir, 'data', '*.*')))]
        environment['BASEMAP_DEPENDENCIES'] = ['geos_c']
        basemap_found = True
    except Exception, e:
        print e
    return basemap_found


def install(target='build', version=None):
    global environment
    if not basemap_found:
        if version is None:
            version = '1.0.5'
        website = 'http://downloads.sourceforge.net/project/matplotlib/' + \
            'matplotlib-toolkits/basemap-' + version + '/'
        archive = 'basemap-' + version + '.tar.gz'
        install_pypkg_locally('basemap-' + version, website, archive, target)
        environment['BASEMAP_VERSION'] = version
        environment['BASEMAP_DATA_PATHLIST'] = basemap_data_pathlist
        basemap_dir = os.path.abspath(os.path.join(target, local_lib_dir,
                                                   'mpl_toolkits', 'basemap'))
        environment['BASEMAP_DIR'] = basemap_dir
        environment['BASEMAP_DATA_FILES'] = \
            [(basemap_data_dir,
              glob.glob(os.path.join(basemap_dir, 'data', '*.*')))]
        environment['BASEMAP_DEPENDENCIES'] = ['geos_c']
        patch(basemap_dir)


def patch(basemap_dir):
    ## modify faulty pyproj data location
    problem_file = os.path.join(basemap_dir, 'pyproj.py')
    print 'PATCH ' + problem_file
    problem_exists = True
    pf = open(problem_file, 'r')
    for line in pf:
        if 'BASEMAPDATA' in line:
            problem_exists = False
            break
    pf.close()
    if problem_exists:
        replacement = \
            "if 'BASEMAPDATA' in os.environ:\n" \
            "    pyproj_datadir = os.environ['BASEMAPDATA']\n" \
            "else:\n" \
            "    pyproj_datadir = "
        try:
            patch_file(problem_file, "pyproj_datadir = ",
                       "pyproj_datadir = ", replacement)
        except IOError:  ## Permission denied
            sys.stderr.write('WARNING: installed basemap package at ' +
                             basemap_dir + ' cannot be relocated. ' +
                             'Most users can ignore this message.')
