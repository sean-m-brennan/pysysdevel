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

import os
import sys
import struct
import glob
import platform

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
        build = self.get_finalized_command('build')
        build_shlib = self.get_finalized_command('build_shlib')
        install = self.get_finalized_command('install')
        self.verbose = util.DEBUG

        if install.prefix is None:
            target_dir = os.path.join(install.install_base, lib)
        else:
            target_dir = os.path.join(install.prefix, lib)
        self.mkpath(target_dir)
        if build_shlib.install_shared_libraries:
            for lib in build_shlib.install_shared_libraries:
                target = target_dir + os.sep
                source = os.path.join(build_shlib.build_clib, lib[1])
                self.copy_file(source, target)

        if self.distribution.extra_install_modules:
            ## prefer updated packages
            local_pkgs_dir = os.path.join(build.build_base, util.local_lib_dir)
            insertions = 0
            if os.path.exists(local_pkgs_dir):
                sys.path.insert(0, os.path.abspath(local_pkgs_dir))
                insertions += 1
                for ent in os.listdir(os.path.abspath(local_pkgs_dir)):
                    if os.path.isdir(os.path.join(local_pkgs_dir, ent)) and \
                            ent[-4:] == '.egg':
                        pth = os.path.join(local_pkgs_dir, ent)
                        sys.path.insert(0, os.path.abspath(pth))
                        insertions += 1

            module_dir = install.install_platlib
            for mod in self.distribution.extra_install_modules:
                source = util.get_module_location(mod, local_pkgs_dir)
                if os.path.isdir(source):
                    self.copy_tree(source, os.path.join(module_dir, mod))
                else:
                    self.copy_file(source, module_dir)
            for i in range(insertions):
                sys.path.pop(0)

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
