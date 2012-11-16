# -*- coding: utf-8 -*-
"""
'install_data' command for installing shared libraries and executables
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

import os, struct

from distutils.command import install_lib
from distutils.util import change_root, convert_path


class install_exe(install_lib.install_lib):
    def run (self):
        '''
        Also install native executables
        '''
        install_lib.install_lib.run(self)

        build_exe = self.get_finalized_command('build_exe')
        install = self.get_finalized_command('install')

        target_dir = os.path.join(install.prefix, 'bin')
        self.mkpath(target_dir)
        for exe in build_exe.install_executables:
            source = os.path.join(build_exe.build_temp, exe)
            self.copy_file(source, target_dir)
