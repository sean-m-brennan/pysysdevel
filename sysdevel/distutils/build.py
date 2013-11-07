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
modified 'build' command
"""

import os
import sys

try:
    from numpy.distutils.command.build import build as old_build
except ImportError:
    from distutils.command.build import build as old_build

from .recur import process_subpackages


class build(old_build):
    '''
    Subclass build command to support new commands.
    '''
    def has_pure_modules(self):
        return self.distribution.has_pure_modules() or \
            self.distribution.has_antlr_extensions() or \
            self.distribution.has_sysdevel_support()

    def has_scripts(self):
        return self.distribution.has_scripts()

    def has_c_libraries(self):
        return self.distribution.has_c_libraries()

    def has_shared_libraries(self):
        return self.distribution.has_shared_libs()

    def has_pypp_extensions(self):
        return self.distribution.has_pypp_extensions()

    def has_web_extensions(self):
        return self.distribution.has_web_extensions()

    def has_documents(self):
        return self.distribution.has_documents()

    def has_executables(self):
        return self.distribution.has_executables()

    def has_data(self):
        return self.distribution.has_data_files() or \
            self.distribution.has_data_directories()


    ## Order is important
    sub_commands = [('config_cc',      lambda *args: True),
                    ('config_fc',      lambda *args: True),
                    ('build_src',      old_build.has_ext_modules),
                    ('build_py',       has_pure_modules),
                    ('build_js',       has_web_extensions),
                    ('build_clib',     has_c_libraries),
                    ('build_shlib',    has_shared_libraries),
                    ('build_ext',      old_build.has_ext_modules),
                    ('build_pypp_ext', has_pypp_extensions),
                    ('build_scripts',  has_scripts),
                    ('build_doc',      has_documents),
                    ('build_exe',      has_executables),
                    ]


    def run(self):
        if self.distribution.subpackages != None:
            if self.get_finalized_command('install').ran:
                return  ## avoid build after install
            try:
                os.makedirs(self.build_base)
            except:
                pass
            for idx in range(len(sys.argv)):
                if 'setup.py' in sys.argv[idx]:
                    break
            argv = list(sys.argv[idx+1:])
            if 'install' in argv:
                argv.remove('install')
            if 'clean' in argv:
                argv.remove('clean')

            #FIXME run dependencies

            process_subpackages(self.distribution.parallel_build, 'build',
                                self.build_base, self.distribution.subpackages,
                                argv, self.distribution.quit_on_error)

            if self.has_pure_modules() or self.has_c_libraries() or \
                    self.has_ext_modules() or self.has_shared_libraries() or \
                    self.has_pypp_extensions() or self.has_web_extensions() or \
                    self.has_documents() or self.has_executables() or \
                    self.has_scripts() or self.has_data():
                old_build.run(self)
        else:
            old_build.run(self)

