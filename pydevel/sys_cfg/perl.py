#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find Perl headers and library
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

import os, platform

from pydevel.util import *

environment = dict()
perl_found = False


def null():
    global environment
    environment['PERL_INCLUDE_DIR'] = None
    environment['PERL_LIBRARY_DIR'] = None
    environment['PERL_LIBRARIES'] = []
    environment['PERL_LIBS'] = []


def is_installed(version=None):
    global environment, perl_found
    perl_core_dir = ''
    try:
        try:
            perl_core_dir = os.environ['PERL_CORE']
        except:
            try:
                perl_core_dir = os.environ['PERL_ROOT']
            except:
                pass
        if perl_core_dir != '':
            _, perl_lib  = find_library('perl', [perl_core_dir], ['perl5'])
            perl_core_dir = find_header('perl.h', [perl_core_dir])
        else:
            base_dirs = []
            if 'windows' in platform.system().lower():
                base_dirs += [os.path.join('c:', 'perl')]
            perl_core_dir, perl_lib  = find_library('perl', base_dirs,
                                                    ['perl5'])
            perl_core_dir = find_header('perl.h', [perl_core_dir])
        environment['PERL_INCLUDE_DIR'] = perl_core_dir
        environment['PERL_LIBRARY_DIR'] = perl_core_dir
        environment['PERL_LIBRARIES'] = [perl_lib]
        environment['PERL_LIBS'] = ['perl']
        perl_found = True
    except Exception,e:
        print e
        perl_found = False
    return perl_found


def install(target='build', version=None):
    ## User must install
    raise Exception('Perl development library required, but not installed.' +
                    '\nTry http://www.perl.org/get.html;' +
                    ' or yum install perl-devel')
