# -*- coding: utf-8 -*-
"""
sysdevel package

The sysdevel package facilitates multi-model simulation development in three
areas: model coupling, data visualization, and collaboration & distribution.
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


__all__ = ['pkg_config', 'core', 'util',
           'build_clib', 'build_doc', 'build_exe', 'build_js',
           'build_pypp_ext', 'build_py', 'build_scripts', 'build_shlib',
           'build_src', 'install_data', 'install_exe', 'install_lib',
           'configure',]

import os

config_dir = os.path.join(os.path.dirname(__file__), 'configure')
support_dir = os.path.join(os.path.dirname(__file__), 'support')

from configure import configure_system, FatalError
