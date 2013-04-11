#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find/install Antlr
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

DEPENDENCIES = ['java']

environment = dict()
antlr_found = False
DEBUG = False


def null():
    global environment
    environment['ANTLR'] = None


def is_installed(environ, version):
    global environment, antlr_found
    if version is None:
        version = '3.1.2'
    set_debug(DEBUG)
    try:
        classpaths = []
        try:
            pathlist = environ['CLASSPATH'].split(_sep_)
            for path in pathlist:
                classpaths.append(os.path.dirname(path))
        except:
            pass
        try:
            antlr_root = os.environ['ANTLR_ROOT']
        except:
            antlr_root = None
        win_locs = []
        for d in programfiles_directories():
            win_locs.append(os.path.join(d, 'ANTLR', 'lib'))
        jarfile = find_file('antlr*' + version[0] + '*.jar',
                            ['/usr/share/java', '/opt/local/share/java',
                             antlr_root,] + win_locs + classpaths)
        environment['ANTLR'] = [environ['JAVA'],
                                "-classpath", os.path.abspath(jarfile),
                                "org.antlr.Tool",]
        antlr_found = True
    except Exception,e:
        if DEBUG:
            print e
    return antlr_found


def install(environ, version, locally=True):
    global environment
    if not antlr_found:
        website = 'http://www.antlr.org/download/'
        if version is None:
            version = '3.1.2'
        if version.startswith('3'):
            website = 'http://www.antlr3.org/download/'
        here = os.path.abspath(os.getcwd())
        src_dir = 'antlr-' + str(version)
        archive = src_dir + '.tar.gz'
        fetch(website, archive, archive)
        unarchive( archive, src_dir)
        jarfile = os.path.join(target_build_dir, src_dir,
                               'lib', src_dir + '.jar')
        ## TODO: global install not implemented
        environment['ANTLR'] = [environ['JAVA'],
                                "-classpath", os.path.abspath(jarfile),
                                "org.antlr.Tool",]
