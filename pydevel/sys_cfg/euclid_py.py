#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find/install Euclid
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

from pydevel.util import *

environment = dict()
euclid_found = False


def null():
    global environment
    environment['EUCLID_VERSION'] = None


def is_installed(version=None):
    global environment, euclid_found
    try:
        import euclid
        euclid_found = True
    except Exception,e:
        print 'Euclid not found: ' + str(e)
    return euclid_found


def install(target='build', version=None):
    global environment
    if not euclid_found:
        website = 'http://pyeuclid.googlecode.com/svn/trunk/'
        src = 'euclid.py'
        install_pyscript_locally(website, src, target)
        environment['EUCLID_VERSION'] = 'latest'
        sys.path.insert(0, os.path.join(target, local_lib_dir))
