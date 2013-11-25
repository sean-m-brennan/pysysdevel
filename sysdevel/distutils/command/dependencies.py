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

from ..prerequisites import RequirementsFinder
from ..configure import configure_system
from ..filesystem import mkdir
from .. import options
from ...util import is_string


class dependencies(Command):
    description = "package dependencies"
    user_options = [('show', 's', 'show the dependencies'),
                    ('show-subpackages', None,
                     'show the dependencies of individual sub-packages'),
                    ('sublevel=', None, 'sub-package level'),]


    def initialize_options(self):
        self.show = False
        self.show_subpackages = False
        self.sublevel = 0
        self.ran = False

    def finalize_options(self):
        if self.sublevel is None:
            self.sublevel = 0
        self.sublevel = int(self.sublevel)
        if self.show_subpackages:
            self.show = True
        self.requirements = []  ## may contain (dep_name, version) tuples


    def run(self):
        self.ran = True
        options.set_top_level(self.sublevel)
        token = 'Package dependencies: '
        outlog = os.path.join(options.target_build_dir, 'config.out')
        errlog = os.path.join(options.target_build_dir, 'config.err')
        if self.sublevel == 0:
            if os.path.exists(outlog):
                os.remove(outlog)
            if os.path.exists(errlog):
                os.remove(errlog)

        if self.distribution.subpackages != None:
            for idx in range(len(sys.argv)):
                if 'setup.py' in sys.argv[idx]:
                    break
            argv = list(sys.argv[idx+1:])
            for arg in sys.argv:
                if '--sublevel' in arg:
                    argv.remove(arg)
            shell=False
            if 'windows' in platform.system().lower():
                shell = True
            for (pkg_name, pkg_dir) in self.distribution.subpackages:
                rf = RequirementsFinder(os.path.join(pkg_dir, 'setup.py'))
                if rf.is_sysdevel_build:  ## depth may be greater than one
                    if rf.needs_early_config:
                        print('Previewing dependencies for ' + pkg_name +
                              ' configuration ...')
                    dep_args = ['dependencies',
                                    '--sublevel=' + str(self.sublevel + 1)]
                    ## do nothing else but check dependencies
                    cmd = [sys.executable, os.path.join(pkg_dir, 'setup.py'),
                           'dependencies',
                           '--sublevel=' + str(self.sublevel + 1)]
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         shell=shell)
                    out, err = p.communicate()
                    out = out.strip()
                    err = err.strip()
                    if not os.path.exists(options.target_build_dir):
                        mkdir(options.target_build_dir)
                    log = open(outlog, 'a')
                    if out:
                        log.write(pkg_name.upper() + ':\n')
                        log.write(out + '\n\n')
                    log.close
                    log = open(errlog, 'a')
                    if err:
                        log.write(pkg_name.upper() + ':\n')
                        log.write(err + '\n\n')
                    log.close()
                    if p.wait() != 0:
                        raise Exception('Dependency check failed for ' +
                                        pkg_name)
                    begin = out.find(token)
                    end = out.find('\n', begin)+1
                    p_list = out[begin+len(token):end]
                    if end == 0:
                        p_list = out[begin+len(token):]
                    self.requirements += p_list.split(',')
                    if self.show_subpackages:
                        print(pkg_name.upper() + ':  ' + p_list)
                else:
                    self.requirements += rf.requires_list
                    if self.show_subpackages:
                        print(pkg_name.upper() + ':  ' +
                              ', '.join(rf.requires_list))
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

        unversioned = list(set([r for r in self.requirements if is_string(r)]))
        versioned = list(set([r for r in self.requirements
                              if not is_string(r)]))
        ## check for tuples w/ duplicate 1st element
        cluster = dict()
        for r in versioned:
            if r[0] in cluster:
                if r[1] > cluster[r[0]]:
                    cluster[r[0]] = r[1]
            else:
                cluster[r[0]] = r[1]
        versioned = cluster.items()
        deps_list = unversioned + [r[0] for r in versioned]
        self.requirements = versioned + unversioned

        if self.sublevel == 0:
            if self.show:
                print(self.distribution.metadata.name + ' ' +
                      token + ', '.join(deps_list))
            if not self.show or 'build' in sys.argv:
                env_old = self.distribution.environment
                env = configure_system(self.requirements,
                                       self.distribution.version)
                self.distribution.environment = dict(list(env_old.items()) +
                                                     list(env.items()))
        else:  ## sysdevel subpackage, collect via stdout (see above)
            print(token + ', '.join(deps_list))
