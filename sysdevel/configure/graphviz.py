#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find Graphviz library
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
graphviz_found = False


def null():
    global environment
    environment['GRAPHVIZ_INCLUDE_DIR'] = None
    environment['GRAPHVIZ_LIB_DIR'] = None
    environment['GRAPHVIZ_LIBRARIES'] = []
    environment['GRAPHVIZ_LIBS'] = []


def is_installed(environ, version):
    global environment, graphviz_found
    base_dirs = []
    try:
        base_dirs.append(os.environ['GRAPHVIZ_ROOT'])
    except:
        pass
    if 'windows' in platform.system().lower():
        try:
            progfiles = os.environ['ProgramFiles']
            base_dirs += glob.glob(os.path.join(progfiles, 'Graphviz*'))
        except:
            pass
        try:
            base_dirs.append(environ['MSYS_DIR'])
        except:
            pass
    try:
        inc_dir = find_header('graph.h', base_dirs, ['graphviz'])
        lib_dir, lib = find_library('graph', base_dirs)
        graphviz_found = True
    except:
        return graphviz_found

    environment['GRAPHVIZ_INCLUDE_DIR'] = inc_dir
    environment['GRAPHVIZ_LIB_DIR'] = lib_dir
    environment['GRAPHVIZ_LIBRARIES'] = [lib]
    environment['GRAPHVIZ_LIBS'] = ['graph']
    return graphviz_found


def install(environ, version, target='build'):
    if not graphviz_found:
        if version is None:
            version = '2.30.1'
        website = ('http://www.graphviz.org/',
                   'pub/graphviz/stable/SOURCES/')
        if 'windows' in platform.system().lower():
            ## assumes MinGW installed and detected
            here = os.path.abspath(os.getcwd())
            src_dir = 'graphviz-' + str(version)
            archive = src_dir + '.tar.gz'
            fetch(''.join(website), archive, archive)
            unarchive(os.path.join(here, download_dir, archive),
                      target, src_dir)
            build_dir = os.path.join(src_dir, '_build')
            mkdir(build_dir)
            os.chdir(build_dir)
            mingw_check_call(environ, ['../configure',
                                       '--prefix=' + environ['MSYS_PREFIX']])
            mingw_check_call(environ, ['make'])
            mingw_check_call(environ, ['make', 'install'])
            os.chdir(here)
        else:
            global_install('Graphviz', website,
                           None,
                           'graphviz-devel',
                           'graphviz-dev',
                           'graphviz-devel')
        if not is_installed(environ, version):
            raise Exception('Graphviz installation failed.')
