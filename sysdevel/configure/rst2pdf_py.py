#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find rst2pdf
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

from sysdevel.util import *

DEPENDENCIES = ['docutils', 'reportlab', 'pygments', 'pdfrw']

environment = dict()
rst2pdf_found = False


def null():
    pass


def is_installed(environ, version):
    global environment, rst2pdf_found
    try:
        import rst2pdf
        ver = rst2pdf.version
        if compare_versions(ver, version) == -1:
            return rst2pdf_found
        rst2pdf_found = True
    except:
        pass
    return rst2pdf_found


def install(environ, version, locally=True):
    if not rst2pdf_found:
        website = 'http://rst2pdf.googlecode.com/files/'
        if version is None:
            version = '0.93'
        src_dir = 'rst2pdf-' + str(version)
        archive = src_dir + '.tar.gz' 
        install_pypkg(src_dir, website, archive, locally=locally)
        if not is_installed(environ, version):
            raise Exception('rst2pdf installation failed.')
