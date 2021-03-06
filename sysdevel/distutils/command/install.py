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
modified 'install' command
"""

import os
import sys

# pylint: disable=W0201
try:
    from numpy.distutils.command.install import install as old_install
except ImportError:
    from distutils.command.install import install as old_install

from sysdevel.distutils.recur import process_subpackages
from sysdevel.distutils import options


class install(old_install):
    '''
    Subclass install command to support new commands.
    '''
    user_options = [('sublevel=', None, 'sub-package level'),
                    ] + old_install.user_options

    def initialize_options (self):
        old_install.initialize_options(self)
        self.sublevel = 0
        self.ran = False

    def finalize_options(self):
        old_install.finalize_options(self)
        self.sublevel = int(self.sublevel)


    def has_lib(self):
        return old_install.has_lib(self) or self.distribution.has_shared_libs()

    def has_exe(self):
        return self.distribution.has_executables()

    def has_data(self):
        return self.distribution.has_data_files() or \
            self.distribution.has_data_directories()

    sub_commands = [('install_exe', has_exe),
                    ('install_data', has_data),
                    ('install_lib', has_lib),
                    ('install_headers', old_install.has_headers),
                    ('install_scripts', old_install.has_scripts),
                    #('install_egg_info', lambda self:True),
                    ]

    def run(self):
        deps = self.get_finalized_command('dependencies')
        build = self.get_finalized_command('build')
        level_list = [deps.sublevel, build.sublevel, self.sublevel]
        ## detect malformed usage
        if len(set([l for l in level_list if l])) > 1:
            raise Exception("Multiple sublevels specified.")
        self.sublevel = build.sublevel = deps.sublevel = max(*level_list)

        ## before anything else (runs in case build hasn't run)
        if self.sublevel == 0 and not deps.ran:
            self.run_command('dependencies')

        options.set_top_level(self.sublevel)
        if self.distribution.subpackages != None:
            try:
                os.makedirs(build.build_base)
            except OSError:
                pass
            idx = 0
            for i in range(len(sys.argv)):
                idx = i
                if 'setup.py' in sys.argv[idx]:
                    break
            argv = list(sys.argv[idx+1:])
            for arg in sys.argv:
                if arg == 'build' or \
                   arg == 'clean' or \
                   '--sublevel' in arg:
                    argv.remove(arg)

            argv += ['--sublevel=' + str(self.sublevel + 1)]
            process_subpackages(build.distribution.parallel_build, 'install',
                                build.build_base, self.distribution.subpackages,
                                argv, build.distribution.quit_on_error)

            if build.has_pure_modules() or build.has_c_libraries() or \
                    build.has_ext_modules() or build.has_shared_libraries() or \
                    build.has_pypp_extensions() or \
                    build.has_web_extensions() or \
                    build.has_documents() or build.has_executables() or \
                    build.has_scripts() or build.has_data():
                old_install.run(self)
        else:
            old_install.run(self)
        self.ran = True
