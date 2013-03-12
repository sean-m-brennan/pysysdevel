#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find GCCXML
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

import os, subprocess

from sysdevel.util import *

environment = dict()
gccxml_found = False


def null():
    global environment
    environment['GCCXML'] = None


def is_installed(version=None):
    global environment, gccxml_found
    base_dirs = []
    try:
        progfiles = os.environ['ProgramFiles']
        base_dirs.append(os.path.join(progfiles, 'GCC_XML', 'bin'))
    except:
        pass
    try:
        base_dirs.append(os.path.join(environment['MSYS_DIR'], 'bin'))
    except:
        pass
    try:
        environment['GCCXML'] = find_program('gccxml', base_dirs)
        gccxml_found = True
    except:
        pass
    return gccxml_found


def install(target='build', version=None):
    if not gccxml_found:
        if compare_versions(version, '0.6') == 1 and \
                'GIT' in environment.keys() and \
                'CMAKE' in environment.keys() and \
                'windows' in platform.system().lower():
            ## assumes MinGW, git, and cmake are installed and detected
            here = os.path.abspath(os.getcwd())
            src_dir = 'gccxml'
            os.chdir(download_dir)
            gitsite = 'https://github.com/gccxml/gccxml.git'
            subprocess.check_call([environment['GIT'],
                                   'clone', gitsite, src_dir])
            build_dir = os.path.join(download_dir, src_dir, '_build')
            mkdir(build_dir)
            os.chdir(build_dir)
            subprocess.check_call([environment['MSYS_SHELL'], 
                                   environment['CMAKE'], '..',
                                   '-G', '"MSYS Makefiles"',
                                   '-DCMAKE_INSTALL_PREFIX=' + \
                                       environment['MSYS_DIR'],
                                   '-DCMAKE_MAKE_PROGRAM=/bin/make.exe'])
            subprocess.check_call([environment['MSYS_SHELL'], 'make'])
            subprocess.check_call([environment['MSYS_SHELL'],
                                   'make', 'install'])
            os.chdir(here)
        else:
            if version is None:
                version = '0.6.0'
            website = ('http://www.gccxml.org/',
                       'files/v' + major_minor_version(version) + '/')
            global_install('GCCXML', website,
                           'gccxml-' + str(version) + '-win32.exe',
                           'gccxml-devel',
                           'gccxml',
                           'gccxml')
        is_installed()
