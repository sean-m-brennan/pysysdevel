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
'dependencies' command for printing a list of all dependencies for this setup
"""

INTERLEAVED_OUTPUT = True


import os
import sys
from distutils.core import Command

from sysdevel.distutils.configure import configure_system
from sysdevel.distutils.dependency_graph import get_dep_dag
from sysdevel.distutils import options


# pylint: disable=W0201
class dependencies(Command):
    description = "package dependencies"
    user_options = [('sublevel=', None, 'sub-package level'),
                    ('show', 's', 'show the dependencies'),
                    ('system-install', None,
                     'system-wide installation of dependencies'),
                    ('download', None,
                     'download all listed dependencies'),
                    ('download-dir=', None,
                     'set the third-party software download directory')]

    def initialize_options(self):
        self.show = False
        self.system_install = False
        self.download = False
        self.log_only = False
        self.ran = False
        self.download_dir = options.default_download_dir
        self.sublevel = 0

    def finalize_options(self):
        self.sublevel = int(self.sublevel)
        if self.download_dir[-1] == '/' or self.download_dir[-1] == '\\':
            self.download_dir = self.download_dir[:-1]
        options.set_download_dir(os.path.basename(self.download_dir))
        self.requirements = []  ## may contain (dep_name, version) tuples

    def run(self):
        build = self.get_finalized_command('build')
        install = self.get_finalized_command('install')
        level_list = [self.sublevel, build.sublevel, install.sublevel]
        ## detect malformed usage
        if len(set([l for l in level_list if l])) > 1:
            raise Exception("Multiple sublevels specified.")
        self.sublevel = build.sublevel = install.sublevel = max(*level_list)

        dep_graph = get_dep_dag(os.getcwd())  ## assumes cwd is setup dir
        if self.show:
            print dep_graph
            sys.exit(0)

        ts = dep_graph.topological_sort()[:-1]
        if self.distribution.subpackages != None:
            for pkg_name, _ in self.distribution.subpackages:
                for dep in dep_graph.adjacency_list().keys():
                    if pkg_name == dep or \
                       (isinstance(dep, tuple) and pkg_name == dep[0]):
                        ts.remove(dep)
        self.requirements += ts
        req_modules = [r[0] if isinstance(r, tuple) else r
                       for r in self.requirements]
        self.distribution.extra_install_modules += req_modules
        env_old = self.distribution.environment
        options.set_top_level(self.sublevel)
        env = configure_system(self.requirements, self.distribution.version,
                               install=(not self.download),
                               locally=(not self.system_install),
                               download=self.download)
        self.distribution.environment = dict(list(env_old.items()) +
                                             list(env.items()))
        self.ran = True
