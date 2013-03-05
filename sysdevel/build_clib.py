# -*- coding: utf-8 -*-
"""
'build_clib' command with conditional recompile
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
from numpy.distutils.command.build_clib import build_clib as old_build_clib
from numpy.distutils.misc_util import get_numpy_include_dirs


class build_clib(old_build_clib):
    '''
    Build static libraries for use in Python extensions
    '''
    def finalize_options (self):
        old_build_clib.finalize_options(self)
        ## prevent collision
        self.build_temp = os.path.join(self.build_temp, 'static')


    def build_libraries(self, libraries):
        if self.libraries and len(self.libraries) > 0:
            for (lib_name, build_info) in libraries:
                ## Special defines
                env = self.distribution.environment
                key = lib_name + '_DEFINES'
                if env and key in env:
                    extra_preargs = build_info.get('extra_compiler_args') or []
                    install_data = self.get_finalized_command('install_data')
                    for define in env[key]:
                        template = define[0]
                        insert = util.safe_eval(define[1])
                        arg = template.replace('@@def@@', insert)
                        extra_preargs.append(template)
                    build_info['extra_compiler_args'] = extra_preargs

                ## Conditional recompile
                target_library = 'lib' + \
                    self.compiler.library_filename(lib_name, output_dir='')
                target_path = os.path.join(self.build_clib, target_library)
                recompile = False
                if not os.path.exists(target_path) or self.force:
                    recompile = True
                else:
                    for src in build_info.get('sources'):
                        if os.path.getmtime(target_path) < os.path.getmtime(src):
                            recompile = True
                            break
                if not recompile:
                    continue

                self.build_a_library(build_info, lib_name, libraries)
