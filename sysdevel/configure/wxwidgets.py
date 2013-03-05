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

import os, subprocess

from sysdevel.util import *

environment = dict()
wx_found = False


def null():
    global environment
    environment['WX_CPP_FLAGS'] = []
    environment['WX_LD_FLAGS'] = []


def is_installed(version=None):
    global environment, wx_found
    try:
        wx_config = os.environ['WX_CONFIG']
    except:
        try:
            wx_config = find_program('wx-config')
        except:
            return False
    cppflags_cmd = [wx_config, '--cppflags']
    process = subprocess.Popen(cppflags_cmd, stdout=subprocess.PIPE)
    environment['WX_CPP_FLAGS'] = process.communicate()[0].split()

    ldflags_cmd = [wx_config, '--libs', '--gl-libs', '--static=no']
    process = subprocess.Popen(ldflags_cmd, stdout=subprocess.PIPE)
    environment['WX_LD_FLAGS'] = process.communicate()[0].split()
    return True
    

def install(target='build', version=None):
    if not wx_found:
        raise Exception('WxWidgets not found. (include=' +
                        str(environment['WX_CPP_FLAGS']) + ', library=' +
                        str(environment['WX_LD_FLAGS']) + ')')
