"""
Copyright 2013.  Los Alamos National Security, LLC.
This material was produced under U.S. Government contract
DE-AC52-06NA25396 for Los Alamos National Laboratory (LANL), which is
operated by Los Alamos National Security, LLC for the U.S. Department
of Energy. The U.S. Government has rights to use, reproduce, and
distribute this software.  NEITHER THE GOVERNMENT NOR LOS ALAMOS
NATIONAL SECURITY, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
modified to produce derivative works, such modified software should be
clearly marked, so as not to confuse it with the version available
from LANL.

Licensed under the Mozilla Public License, Version 2.0 (the
"License"); you may not use this file except in compliance with the
License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/2.0/

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing
permissions and limitations under the License.
"""
# pylint: disable=W0105
"""
'build_shlib' command for *shared* (non-python) libraries
"""

import os

# pylint: disable=W0201
have_numpy = False
try:
    from numpy.distutils.command.build_clib import build_clib
    have_numpy = True
except ImportError:
    from distutils.command.build_clib import build_clib

from sysdevel.distutils.building import safe_eval, build_target, SHARED_LIBRARY


class build_shlib(build_clib):
    '''
    Build *shared* libraries for use in Python extensions
    '''
    def finalize_options(self):
        build_clib.finalize_options(self)
        self.libraries = self.distribution.sh_libraries
        self.install_shared_libraries = []
        ## prevent collision
        self.build_temp = os.path.join(self.build_temp, 'shared')
        if self.libraries and len(self.libraries) > 0:
            self.check_library_list(self.libraries)
            from distutils.ccompiler import new_compiler
            compiler = new_compiler(compiler=self.compiler)
            compiler.customize(self.distribution,
                               need_cxx=self.have_cxx_sources())
            #static_libraries = self.distribution.libraries
            for lib in self.libraries:
                target_lib = compiler.library_filename(lib[0],
                                                       lib_type='shared',
                                                       output_dir='')
                self.install_shared_libraries.append((lib[1]['package'],
                                                      target_lib))

    def build_libraries(self, libraries):
        if self.libraries and len(self.libraries) > 0:
            for (lib_name, build_info) in libraries:
                ## Special defines
                env = self.distribution.environment
                key = lib_name + '_DEFINES'
                if env and key in env:
                    extra_preargs = build_info.get('extra_compiler_args') or []
                    for define in env[key]:
                        template = define[0]
                        insert = safe_eval(define[1])
                        arg = template.replace('@@def@@', insert)
                        extra_preargs.append(arg)
                    build_info['extra_compiler_args'] = extra_preargs
                if build_info.get('mpi', False):
                    self.build_temp = os.path.join(self.build_temp, 'mpi')
                self.build_a_library(build_info, lib_name, libraries)


    def build_a_library(self, build_info, lib_name, libraries):
        build_target(self, build_info, lib_name, SHARED_LIBRARY)
