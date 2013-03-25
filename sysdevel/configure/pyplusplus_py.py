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

from sysdevel.util import *

DEPENDENCIES = ['gccxml']

environment = dict()
pyplusplus_found = False


def null():
    pass


def is_installed(environ, version):
    global pyplusplus_found
    try:
        import pyplusplus
        pyplusplus_found = True
    except Exception,e:
        print 'Py++ not found: ' + str(e)
    return pyplusplus_found


def install(environ, version, target='build', locally=True):
    global environment
    if not pyplusplus_found:
        if version is None:
            version = '1.0.0'
        mainsite = 'http://downloads.sourceforge.net/project/pygccxml/'
        website = mainsite + 'pygccxml/pygccxml-' + version[:-2] + '/'
        src_dir = 'pygccxml-' + str(version)
        archive = src_dir + '.zip'
        install_pypkg(src_dir, website, archive, target, locally=locally)

        website = mainsite + 'pyplusplus/pyplusplus-' + version[:-2] + '/'
        src_dir = 'pyplusplus-' + str(version) + '.zip'
        archive = src_dir + '.zip'
        install_pypkg(src_dir, website, archive, target, locally=locally)
        if not is_installed(environ, version):
            raise Exception('Py++ installation failed.')
