#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find F2C
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
f2c_found = False


def is_installed():
    global environment, f2c_found
    ## look for it
    try:
        incl_dir = find_header('f2c.h')
        environment['F2C_INCLUDE_DIR'] = incl_dir
        #environment['F2C_LIB_DIR'], lib = find_library('f2c')
        #environment['F2C_LIBRARY'] = 'f2c'
        f2c_found = True
    except:
        pass
    return f2c_found


def install(target='build'):
    global environment

    website = 'http://www.netlib.org/f2c/'
    here = os.path.abspath(os.getcwd())
    abs_target = os.path.abspath(target)
    if not f2c_found:
        try:
            import urllib, tarfile, subprocess
            download_file = 'f2c.h'
            set_downloading_file(website + download_file)
            if not os.path.exists(target):
                os.makedirs(target)
            os.chdir(target)
            if not os.path.exists(download_file):
                urllib.urlretrieve(website + download_file, download_file,
                                   download_progress)
                print ''
            ## TODO: download/build libf2c
            os.chdir(here)
        except Exception, e:
            os.chdir(here)
            raise Exception('F2C not found. (include=' +
                            str(environment['F2C_INCLUDE_DIR']) + ') ' + str(e))
