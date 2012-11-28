#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find/install Py++/PyGCCXML
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
pyplusplus_found = False


def null():
    global environment
    environment['PYPLUSPLUS_VERSION'] = None


def is_installed():
    global environment, pyplusplus_found
    try:
        import pyplusplus
        try:
            environment['PYPLUSPLUS_VERSION'] = pyplusplus.__version__
        except:
            pass
        pyplusplus_found = True
    except Exception,e:
        print 'Py++ not found: ' + str(e)
    return pyplusplus_found


def install(target='build'):
    global environment
    if not pyplusplus_found:
        website = 'http://prdownloads.sourceforge.net/pygccxml/'
        ver = '1.0.0'
        archive = 'pygccxml-' + ver + '.zip'
        install_pypkg_locally('pygccxml-' + ver, website, archive, target)

        archive = 'pyplusplus-' + ver + '.zip'
        install_pypkg_locally('pyplusplus-' + ver, website, archive, target)
        environment['PYPLUSPLUS_VERSION'] = ver
