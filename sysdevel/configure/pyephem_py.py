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

from sysdevel.util import *

environment = dict()
pyephem_found = False


def null():
    pass


def is_installed(environ, version):
    global pyephem_found
    try:
        import ephem
        ver = ephem.__version__
        if compare_versions(ver, version) == -1:
            return pyephem_found
        pyephem_found = True
    except Exception,e:
        pass
    return pyephem_found


def install(environ, version, target='build', locally=True):
    if not pyephem_found:
        website = 'http://pypi.python.org/packages/source/p/pyephem/'
        if version is None:
            version = '3.7.5.1'
        src_dir = 'pyephem-' + str(version)
        archive = src_dir + '.tar.gz'
        install_pypkg(src_dir, website, archive, target, locally=locally)
        if not is_installed(environ, version):
            raise Exception('ephem installation failed.')
