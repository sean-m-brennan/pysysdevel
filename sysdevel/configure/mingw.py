#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find/fetch/install MinGW
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
import platform

from sysdevel.util import *

environment = dict()
mingw_found = False
DEBUG = False


def null():
    global environment
    environment['MINGW_DIR'] = None
    environment['MSYS_DIR'] = None
    environment['MSYS_SHELL'] = None
    environment['MINGW_CC'] = None
    environment['MINGW_CXX'] = None
    environment['MINGW_FORTRAN'] = None


def is_installed(environ, version):
    global environment, mingw_found
    set_debug(DEBUG)
    if 'MSVC' in environ:
        raise Exception('MinGW *and* MS Visual C both specified ' +
                        'as the chosen compiler.')

    try:
        mingw_root = os.environ['MINGW_ROOT']
    except:
        locations = [os.path.join('C:', os.sep, 'MinGW')]
        for d in programfiles_directories():
            locations.append(os.path.join(d, 'MinGW'))
        try:
            gcc = find_program('mingw32-gcc', locations)
            mingw_root = os.path.abspath(os.path.join(os.path.dirname(gcc), '..'))
        except Exception, e:
            if DEBUG:
                print e
            return mingw_found

    msys_root = os.path.join(mingw_root, 'msys', '1.0')
    try:
        gcc = find_program('mingw32-gcc', [mingw_root])
        gxx = find_program('mingw32-g++', [mingw_root])
        gfort = find_program('mingw32-gfortran', [mingw_root])
        mingw_found = True
    except Exception, e:
        if DEBUG:
            print e
        return mingw_found

    environment['MINGW_DIR']     = mingw_root
    environment['MSYS_DIR']      = msys_root
    environment['MINGW_CC']      = gcc
    environment['MINGW_CXX']     = gxx
    environment['MINGW_FORTRAN'] = gfort
    return mingw_found


def install(environ, version, locally=True):
    if not mingw_found:
        if not 'windows' in platform.system().lower():
            raise Exception('Not installing MinGW on this platform. ' +
                            'Cross compiling not (yet) supported.')
        if version is None:
            version = '20120426'
        website = ('http://sourceforge.net/projects/mingw/',
                   'files/Installer/mingw-get-inst/mingw-get-inst-' +
                   str(version) + '/')
        global_install('MinGW', website,
                       winstaller='mingw-get-inst-' + str(version) + '.exe')
        if not is_installed(environ, version):
            raise Exception('MinGW installation failed.')
