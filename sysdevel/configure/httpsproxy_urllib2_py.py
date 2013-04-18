#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
If we're running Python 2.4/5, pull this patched urllib2. 
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

from sysdevel.util import *

environment = dict()
urllib_patch_found = False


def null():
    pass


def is_installed(environ, version):
    global urllib_patch_found
    pyver = get_python_version()
    if pyver[0] == '2' and (pyver[1] == '4' or pyver[1] == '5'):
        ## Cannot detect if this is already present, install regardless
        urllib_patch_found = False
    else:
        ## Not needed for Python 2.6+
        urllib_patch_found = True
    return urllib_patch_found


def install(environ, version, locally=True):
    if not urllib_patch_found:
        website = 'https://pypi.python.org/packages/source/h/httpsproxy_urllib2/'
        if version is None:
            version = '1.0'
        src_dir = 'httpsproxy_urllib2-' + str(version)
        archive = src_dir + '.tar.gz' 
        install_pypkg(src_dir, website, archive, locally=locally)
        if not is_installed(environ, version):
            raise Exception('urllib patch installation failed.')
