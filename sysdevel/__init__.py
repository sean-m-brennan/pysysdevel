# -*- coding: utf-8 -*-
"""
Entry point for custom packaging
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


__all__ = ['pkg_config', 'core',
           'build_clib', 'build_doc', 'build_exe', 'build_js',
           'build_pypp_ext', 'build_py', 'build_shlib', 'build_src',
           'install_data', 'install_exe', 'install_lib',
           'util', 'httplib', 'urllib2',
           'configure',]

import os
import sys

class FatalError(SystemExit):
    """
    Uncatchable error, exits uncleanly.
    """
    def __init__(self, what):
        sys.stderr.write('FatalError: ' + what + '\n')
        sys.stderr.flush()
        os._exit(-1)
