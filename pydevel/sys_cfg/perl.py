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
    core_dir = ''
    lib_ver = ''
    try:
        if version is None:
            ver = '5'
        else:
            ver = version.split('.')[0]
        if 'windows' in platform.system().lower():
            ver = ''
        try:
            core_dir = os.environ['PERL_CORE']
        except:
            try:
                core_dir = os.environ['PERL_ROOT']
            except:
                pass
        if core_dir != '':
            perl_exe = find_program('perl', [core_dir])
            _, perl_lib  = find_library('perl', [core_dir], ['perl' + ver])
            core_dir = find_header('perl.h', [core_dir])
        else:
            base_bin_dirs = []
            base_lib_dirs = []
            if 'windows' in platform.system().lower():
                ## assumes Strawberry Perl from http://strawberryperl.com
                perl_base = os.path.join('c:', os.sep, 'strawberry', 'perl')
                base_bin_dirs += [os.path.join(perl_base, 'bin')]
                base_lib_dirs += [os.path.join(perl_base, 'lib', 'CORE')]
            perl_exe = find_program('perl', base_bin_dirs)
            core_dir, perl_lib  = find_library('perl', base_lib_dirs,
                                               ['perl' + ver])
            if 'windows' in platform.system().lower():
                lib_ver = perl_lib.split('.')[0].split('perl')[1]
            core_dir = find_header('perl.h', [core_dir])
        environment['PERL_PATH'] = perl_exe
        environment['PERL_INCLUDE_DIR'] = core_dir
        environment['PERL_LIBRARY_DIR'] = core_dir
        environment['PERL_LIBRARIES'] = [perl_lib]
        environment['PERL_LIBS'] = ['perl' + lib_ver]
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
