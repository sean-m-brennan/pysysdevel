#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find wxWidgets library
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
import subprocess
import platform

from sysdevel.util import *

environment = dict()
wx_found = False
DEBUG = False


def null():
    global environment
    environment['WX_CPP_FLAGS'] = []
    environment['WX_LD_FLAGS'] = []


def is_installed(environ, version):
    global environment, wx_found
    set_debug(DEBUG)
    try:
        wx_config = os.environ['WX_CONFIG']
    except:
        locations = []
        try:
            locations.append(environ['MSYS_DIR'])
        except:
            pass
        try:
            wx_config = find_program('wx-config', locations)
        except Exception, e:
            if DEBUG:
                print e
            return wx_found
    try:
        cppflags_cmd = [wx_config, '--cppflags']
        process = subprocess.Popen(cppflags_cmd, stdout=subprocess.PIPE)
        environment['WX_CPP_FLAGS'] = process.communicate()[0].split()

        ldflags_cmd = [wx_config, '--libs', '--gl-libs', '--static=no']
        process = subprocess.Popen(ldflags_cmd, stdout=subprocess.PIPE)
        environment['WX_LD_FLAGS'] = process.communicate()[0].split()
        wx_found = True
    except Exception, e:
        if DEBUG:
            print e
    return wx_found
    

def install(environ, version, locally=True):
    if not wx_found:
        if version is None:
            version = '2.8.12'
        website = ('http://prdownloads.sourceforge.net/wxwindows/',)
        if locally or 'windows' in platform.system().lower():
            src_dir = 'wxMSW-' + str(version)
            archive = src_dir + '.zip'
            autotools_install(environ, website, archive, src_dir, locally)
        else:
            global_install('wxWidgets', website,
                           brew='wxmac', port='wxgtk',
                           deb='libwxbase-dev libwxgtk-dev',
                           rpm='wxBase wxGTK-devel')
        if not is_installed(environ, version):
            raise Exception('WxGTK installation failed.')
