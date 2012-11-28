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

import os

from pydevel.util import *

environment = dict()
graphviz_found = False


def null():
    global environment
    environment['GRAPHVIZ_INCLUDE_DIR'] = None
    environment['GRAPHVIZ_LIBRARY_DIR'] = None
    environment['GRAPHVIZ_LIBRARY'] = None


def is_installed():
    global environment, graphviz_found
    graphviz_dev_dir = ''
    try:
        try:
            graphviz_dev_dir = os.environ['GRAPHVIZ_ROOT']
        except:
            pass
        if graphviz_dev_dir != '':
            graphviz_lib_dir, graphviz_lib  = find_library('graph',
                                                           [graphviz_dev_dir])
            graphviz_inc_dir = find_header('graphviz_version.h',
                                           [graphviz_dev_dir], ['graphviz'])
        else:
            base_dirs = []
            if 'windows' in platform.system().lower():
                base_dirs += [os.path.join('c:', 'graphviz')] #FIXME
            graphviz_lib_dir, graphviz_lib  = find_library('graph', base_dirs)
            graphviz_inc_dir = find_header('graphviz_version.h', base_dirs,
                                           ['graphviz'])
        environment['GRAPHVIZ_INCLUDE_DIR'] = graphviz_inc_dir
        environment['GRAPHVIZ_LIBRARY_DIR'] = graphviz_lib_dir
        environment['GRAPHVIZ_LIBRARY'] = os.path.join(graphviz_lib_dir, graphviz_lib)
        graphviz_found = True
    except Exception,e:
        print e
        graphviz_found = False
    return graphviz_found


def install(target='build'):
    ## User must install
    raise Exception('Graphviz library required, but not installed.' +
                    '\nTry http://www.graphviz.org/Download.php;' +
                    ' or yum install graphviz-devel')
