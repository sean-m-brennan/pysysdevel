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

"""
'build_clib' command with conditional recompile
"""

import os

try:
    from numpy.distutils.command.build_clib import build_clib as old_build_clib
except:
    from distutils.command.build_clib import build_clib as old_build_clib

from .building import safe_eval


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
                        insert = safe_eval(define[1])
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
