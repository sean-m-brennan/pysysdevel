#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find Reportlab
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

environment = dict()
reportlab_found = False


def null():
    pass


def is_installed(environ, version):
    global environment, reportlab_found
    try:
        import reportlab
        ver = reportlab.Version
        if compare_versions(ver, version) == -1:
            return reportlab_found
        reportlab_found = True
    except:
        pass
    return reportlab_found


def install(environ, version, locally=True):
    if not reportlab_found:
        website = 'https://pypi.python.org/packages/source/r/reportlab/'
        if version is None:
            version = '2.3'
            src_dir = 'ReportLab_2_3'
        else:
            src_dir = 'reportlab-' + str(version)
        name = 'reportlab-' + str(version)
        archive = name + '.tar.gz' 
        install_pypkg(name, website, archive, src_dir=src_dir,
                      patch=patch, locally=locally)
        if not is_installed(environ, version):
            raise Exception('Reportlab installation failed.')


def patch(src_path):
    ##FIXME problems with Python 2.4 patch:
    # reportlab/graphics/charts/axes.py
    #  pmv = self._pmv if self.labelAxisMode=='axispmv' else None
    # reportlab/graphics/renderSVG.py
    #  svgAttrs = self.fontHacks[font] if font in self.fontHacks else {}
    pass
