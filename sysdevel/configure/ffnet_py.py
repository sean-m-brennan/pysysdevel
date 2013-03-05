#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find/install ffnet package
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
ffnet_found = False


def null():
    global environment
    environment['FFNET_VERSION'] = None


def is_installed(version=None):
    global environment, ffnet_found
    try:
        import ffnet
        environment['FFNET_VERSION'] = ffnet.version
        ffnet_found = True
    except Exception,e:
        print e
    return ffnet_found


def install(target='build', version=None):
    global environment
    if not ffnet_found:
        if 'windows' in platform.system().lower():
            raise Exception('Install networkx and ffnet from ' + 
                            'http://www.lfd.uci.edu/~gohlke/pythonlibs')
        website = 'http://prdownloads.sourceforge.net/ffnet/'
        if version is None:
            version = '0.7.1'
        archive = 'ffnet-' + version + '.tar.gz'
        install_pypkg_locally('ffnet-' + version, website, archive, target)
        environment['FFNET_VERSION'] = version

        ## also requires networkx
        website = 'http://networkx.lanl.gov/download/networkx/'
        ver = '1.7'
        archive = 'networkx-' + ver + '.tar.gz'
        install_pypkg_locally('networkx-' + ver, website, archive, target)
