# -*- coding: utf-8 -*-
"""
'install_lib' command for installing shared libraries and executables
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

import os, struct, glob, platform

from distutils.command.install_lib import install_lib as old_install_lib
from distutils.util import change_root, convert_path

import util


class install_lib(old_install_lib):
    def run (self):
        '''
        Also install shared libraries and executables
        '''
        old_install_lib.run(self)

        lib = 'lib'
        if struct.calcsize('P') == 8:
            lib = 'lib64'
        build_shlib = self.get_finalized_command('build_shlib')
        install = self.get_finalized_command('install')

        if install.prefix is None:
            target_dir = os.path.join(install.install_base, lib)
        else:
            target_dir = os.path.join(install.prefix, lib)
        self.mkpath(target_dir)
        if build_shlib.install_shared_libraries:
            for lib in build_shlib.install_shared_libraries:
                target = os.path.join(target_dir, lib[0])
                source = os.path.join(build_shlib.build_clib, lib[1])
                self.copy_file(source, target)

        if self.distribution.extra_install_modules:
            for pkg in self.distribution.extra_install_modules:
                source = util.get_module_location(pkg)
                if os.path.isdir(source):
                    self.copy_tree(source, os.path.join(target_dir, pkg))
                else:
                    self.copy_file(source, target_dir)

        if self.distribution.extra_install_libraries:
            for pkg_tpl in self.distribution.extra_install_libraries:
                for lib_tpl in pkg_tpl[1]:
                    libpath = lib_tpl[0]
                    suffixes = ['.so*']
                    prefixes = ['', 'lib']
                    if 'windows' in platform.system().lower():
                        suffixes = ['.dll']
                    elif 'darwin' in platform.system().lower():
                        suffixes += ['.dylib*']
                    for prefix in prefixes:
                        for suffix in suffixes:
                            for libname in lib_tpl[1]:
                                filename = prefix + libname + '*' + suffix
                                for source in glob.glob(os.path.join(libpath,
                                                                     filename)):
                                    self.copy_file(source, target_dir)
