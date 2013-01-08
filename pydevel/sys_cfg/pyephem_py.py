#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find/install Pyephem
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
pyephem_found = False


def null():
    global environment
    environment['PYEPHEM_VERSION'] = None


def is_installed(version=None):
    global environment, pyephem_found
    try:
        import ephem
        ver = ephem.__version__
        if not version is None and ver < version:
            print 'Found pyephem v.' + ver
            return pyephem_found
        environment['PYEPHEM_VERSION'] = ver
        pyephem_found = True
    except Exception,e:
        print 'Pyephem not found: ' + str(e)
    return pyephem_found


def install(target='build', version=None):
    global environment
    if not pyephem_found:
        website = 'http://pypi.python.org/packages/source/p/pyephem/'
        if version is None:
            version = '3.7.5.1'
        archive = 'pyephem-' + version + '.tar.gz'
        install_pypkg_locally('pyephem-' + version, website, archive, target)
        environment['PYEPHEM_VERSION'] = version
