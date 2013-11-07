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
'dependencies' command for printing a list of all dependencies for this setup
"""

import os
import sys
import platform
import subprocess
import inspect
from distutils.core import Command

from .prerequisites import RequirementsFinder
from ..util import is_string


class deps(Command):
    description = "package dependencies"
    user_options = [('show-subpackages', 's',
                     'show the dependencies of individual sub-packages'),
                    ('sublevel=', None, 'sub-package level'),]


    def initialize_options(self):
        self.show_subpackages = False
        self.sublevel = 0

    def finalize_options(self):
        if self.sublevel is None:
            self.sublevel = 0
        self.requirements = []  ## may contain (dep_name, version) tuples


    def run(self):
        token = 'Package dependencies: '
        if self.distribution.subpackages != None:
            for idx in range(len(sys.argv)):
                if 'setup.py' in sys.argv[idx]:
                    break
            argv = list(sys.argv[idx+1:])
            build = self.get_finalized_command('build')
            shell=False
            if 'windows' in platform.system().lower():
                shell = True
            for (pkg_name, pkg_dir) in self.distribution.subpackages:
                rf = RequirementsFinder(os.path.join(pkg_dir, 'setup.py'))
                if rf.is_sysdevel_build:  ## depth may be greater than one
                    p = subprocess.Popen([sys.executable,
                                          os.path.join(pkg_dir, 'setup.py'),
                                         ] + argv + ['--sublevel=' +
                                                     str(self.sublevel + 1)],
                                         stdout=subprocess.PIPE,
                                         shell=shell)
                    out = p.communicate()[0].strip()
                    if p.wait() != 0:
                        raise Exception('Dependency check failed for ' +
                                        pkg_name)
                    p_list = out[out.find(token)+len(token):]
                    if self.show_subpackages:
                        print(pkg_name.upper() + ':  ' + str(p_list))
                    self.requirements += p_list.split(',')
                else:
                    self.requirements += rf.requires_list
            while 'None' in self.requirements:
                self.requirements.remove('None')

        if self.distribution.build_requires:
            self.requirements += self.distribution.build_requires
        if self.distribution.extern_requires:
            self.requirements += self.distribution.extern_requires
        if self.distribution.get_requires():
            self.requirements += list(set(self.distribution.get_requires()))
        if len(self.requirements) == 0:
            self.requirements = ['None']
        self.requirements = list(set(self.requirements))

        #FIXME check for tuples with duplicate elt 0
        deps_list = list(set([r[0] if not is_string(r) else r
                              for r in self.requirements]))
        if self.sublevel == 0:
            if self.show_subpackages:
                print(token + ', '.join(deps_list))
            from sysdevel.distutils import configure_system
            env_old = self.distribution.environment
            env = configure_system(self.requirements, self.distribution.version)
            self.distribution.environment = dict(list(env_old.items()) +
                                                 list(env.items()))
        else:
            print(token + ', '.join(deps_list))
