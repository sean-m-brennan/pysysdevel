#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find Boost
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
boost_found = False


def null():
    global environment
    environment['BOOST_ROOT'] = ''
    environment['BOOST_INCLUDE_DIR'] = ''
    environment['BOOST_LIB_DIR'] = ''
    environment['BOOST_VERSION'] = ''


def is_installed(version=None):
    global environment, boost_found
    if version is None:
        required_version = '1_33'
    else:
        required_version = version.replace('.', '_')

    try:
        ## the easy way
        boost_root = os.environ['BOOST_ROOT']
        boost_root = boost_root.strip('"')
        environment['BOOST_ROOT'] = boost_root
        incl_dir = find_header(os.path.join('boost', 'version.hpp'),
                               [boost_root])
        environment['BOOST_INCLUDE_DIR'] = incl_dir
        try:
            environment['BOOST_LIB_DIR'] = os.environ['BOOST_LIBRARY_DIR']
        except:
            if os.path.exists(os.path.join(boost_root, 'stage', 'lib')):
                environment['BOOST_LIB_DIR'] = os.path.join(boost_root,
                                                            'stage', 'lib')
            else:
                environment['BOOST_LIB_DIR'] = os.path.join(boost_root, 'lib')
        boost_version = get_header_version(os.path.join(incl_dir, 'boost',
                                                        'version.hpp'),
                                           'BOOST_LIB_VERSION')
        boost_version = boost_version.strip('"')
        environment['BOOST_VERSION'] = boost_version
        if boost_version > required_version:
            boost_found = True
    except Exception, e:
        ## look for global machine installation
        environment['BOOST_ROOT'] = None
        win_alt = os.path.normpath(os.path.join('C:', os.sep, 'Boost'))
        incl_dir = find_header(os.path.join('boost', 'python.hpp'),
                               [win_alt], 'boost-*')
        environment['BOOST_INCLUDE_DIR'] = incl_dir
        environment['BOOST_LIB_DIR'], _ = find_library('boost_python',
                                                       [win_alt])
        boost_version = get_header_version(os.path.join(incl_dir, 'boost',
                                                        'version.hpp'),
                                           'BOOST_LIB_VERSION')
        boost_version = boost_version.strip('"')
        environment['BOOST_VERSION'] = boost_version
        if boost_version > required_version:
            boost_found = True
    #print 'Using Boost v.' + boost_version
    return boost_found


def install(target='build', version=None):
    if not boost_found:
        raise Exception('Boost not found. (BOOST_ROOT=' +
                        str(environment['BOOST_ROOT']) + ', include=' +
                        str(environment['BOOST_INCLUDE_DIR']) + ', library=' +
                        str(environment['BOOST_LIB_DIR']) + ', version=' +
                        str(environment['BOOST_VERSION']) + ')')
