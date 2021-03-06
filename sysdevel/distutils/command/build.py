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
modified 'build' command
"""

import os
import sys

# pylint: disable=W0201
try:
    from numpy.distutils.command.build import build as old_build
except ImportError:
    from distutils.command.build import build as old_build

from sysdevel.distutils.recur import process_subpackages
from sysdevel.distutils import options


class build(old_build):
    '''
    Subclass build command to support new commands.
    '''
    user_options = [('sublevel=', None, 'sub-package level'),
                    ] + old_build.user_options

    def initialize_options (self):
        old_build.initialize_options(self)
        self.sublevel = 0
        self.ran = False

    def finalize_options(self):
        old_build.finalize_options(self)
        self.sublevel = int(self.sublevel)
        if self.build_base[-1] == '/' or self.build_base[-1] == '\\':
            self.build_base = self.build_base[:-1]
        options.set_build_dir(os.path.basename(self.build_base))

    def has_pure_modules(self):
        return self.distribution.has_pure_modules() or \
            self.distribution.has_antlr_extensions() or \
            self.distribution.has_sysdevel_support()

    def has_scripts(self):
        return self.distribution.has_scripts()

    def has_sources(self):
        return self.distribution.has_sources()

    def has_c_libraries(self):
        return self.distribution.has_c_libraries()

    def has_shared_libraries(self):
        return self.distribution.has_shared_libs()

    def has_pypp_extensions(self):
        return self.distribution.has_pypp_extensions()

    def has_web_extensions(self):
        return self.distribution.has_web_extensions()

    def has_executables(self):
        return self.distribution.has_executables()

    def has_data(self):
        return self.distribution.has_data_files() or \
            self.distribution.has_data_directories()

    def has_documents(self):
        return self.distribution.has_documents()


    ## Order is important
    sub_commands = [('config_cc',      lambda *args: True),
                    ('config_fc',      lambda *args: True),
                    ('build_src',      has_sources),
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
        deps = self.get_finalized_command('dependencies')
        install = self.get_finalized_command('install')
        level_list = [deps.sublevel, self.sublevel, install.sublevel]
        ## detect malformed usage
        if len(set([l for l in level_list if l])) > 1:
            raise Exception("Multiple sublevels specified.")
        level = max(self.sublevel, install.sublevel, deps.sublevel)
        self.sublevel = install.sublevel = deps.sublevel = max(*level_list)

        ## before anything else
        if self.sublevel == 0 and not deps.ran:
            self.run_command('dependencies')

        options.set_top_level(self.sublevel)
        if self.distribution.subpackages != None:
            install = self.get_finalized_command('install')
            if install.ran:
                return  ## avoid build after install
            for cmd in install.get_sub_commands():
                if getattr(cmd, 'ran', False):
                    return
                ## TODO avoid build after any install_* cmd
            try:
                os.makedirs(self.build_base)
            except OSError:
                pass
            idx = 0
            for i in range(len(sys.argv)):
                idx = i
                if 'setup.py' in sys.argv[idx]:
                    break
            argv = list(sys.argv[idx+1:])
            for arg in sys.argv:
                if arg == 'clean' or '--sublevel' in arg:
                    argv.remove(arg)

            argv += ['--sublevel=' + str(self.sublevel + 1)]
            process_subpackages(self.distribution.parallel_build, 'build',
                                self.build_base, self.distribution.subpackages,
                                argv, self.distribution.quit_on_error)

        old_build.run(self)
        self.ran = True
