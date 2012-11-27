#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find Perl headers and library
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
perl_found = False


def is_installed():
    global environment, perl_found
    try:
        perl_dev_dir, perl_lib  = find_library('perl', [],
                                               [os.path.join('perl4', 'CORE'),
                                                os.path.join('perl5', 'CORE'),])
        environment['PERL_INCLUDE_DIR'] = perl_dev_dir
        environment['PERL_LIBRARY_DIR'] = perl_dev_dir
        environment['PERL_LIBRARY'] = os.path.join(perl_dev_dir, perl_lib)
        perl_found = True
    except Exception,e:
        perl_found = False
    return perl_found



def install(target='build'):
    global environment
    raise "Perl development library required, but not installed."
