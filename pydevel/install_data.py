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

import os
import util

from numpy.distutils.command.install_data import install_data as old_data


class install_data(old_data):
    def initialize_options(self):
        old_data.initialize_options(self)
        self.data_dirs = self.distribution.data_dirs
        if self.data_files is None:
            self.data_files = []
        install = self.get_finalized_command('install')
        if install.prefix is None:
            self.data_install_dir = os.path.join(install.install_base, 'share')
        else:
            self.data_install_dir = os.path.join(install.prefix, 'share')
 

    def run (self):
        old_data.run(self)
        if not hasattr(self.distribution, 'using_py2exe') or \
                not self.distribution.using_py2exe:
           for tpl in self.data_dirs:
                target = os.path.join(self.data_install_dir, tpl[0])
                for d in tpl[1]:
                    util.copy_tree(d, target, excludes=['.svn*', 'CVS*',
                                                        'Makefile*'])
