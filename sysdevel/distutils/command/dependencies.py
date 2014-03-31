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
import platform
import subprocess
from distutils.core import Command

from ..prerequisites import RequirementsFinder
from ..configure import configure_system
from ..filesystem import mkdir
from .. import options
from ...util import is_string

if INTERLEAVED_OUTPUT:
    #pylint: disable=W0611
    from threading import Thread
    try:
        ## Python 3.x
        # pylint: disable=F0401
        from queue import Queue
    except ImportError:
        from Queue import Queue


    def enqueue_output(out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()


# pylint: disable=W0201
class dependencies(Command):
    description = "package dependencies"
    user_options = [('show', 's', 'show the dependencies'),
                    ('show-subpackages', None,
                     'show the dependencies of individual sub-packages'),
                    ('sublevel=', None, 'sub-package level'),
                    ('system-install', None,
                     'system-wide installation of dependencies'),]


    def initialize_options(self):
        self.show = False
        self.show_subpackages = False
        self.system_install = False
        self.sublevel = 0
        self.log_only = False
        self.ran = False

    def finalize_options(self):
        if self.sublevel is None:
            self.sublevel = 0
        self.sublevel = int(self.sublevel)
        if self.show_subpackages:
            self.show = True
        self.requirements = []  ## may contain (dep_name, version) tuples


    def run(self):
        options.set_top_level(self.sublevel)
        token = 'Package dependencies: '
        logfile = os.path.join(options.target_build_dir, 'config.log')
        if self.sublevel == 0:
            if os.path.exists(logfile):
                os.remove(logfile)

        if self.distribution.subpackages != None:
            idx = 0
            for i in range(len(sys.argv)):
                idx = i
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
                if not rf.is_sysdevel_build:
                    ## not sysdevel, look in setup.py 'requires' keyword
                    self.requirements += rf.requires_list
                    if self.show_subpackages:
                        print(pkg_name.upper() + ':  ' +
                              ', '.join([r if is_string(r) else r[0]
                                         for r in rf.requires_list]))
                else:
                    ##FIXME
                    cmd = [sys.executable, os.path.join(pkg_dir, 'setup.py'),
                           ] + argv + ['--sublevel=' + str(self.sublevel + 1)]
                    p = subprocess.Popen(cmd,
                                         stdout=subprocess.PIPE,
                                         shell=shell)
                    out = p.communicate()[0].strip()
                    if p.wait() != 0:
                        raise Exception('Dependency check failed for ' +
                                        pkg_name)
                    p_list = out[out.find(token)+len(token):]
                    if self.show_subpackages:
                        print(pkg_name.upper() + ': ' + str(p_list))
                    self.requirements += p_list.split(',')

                    '''
                    if rf.needs_early_config:
                        print('Dependencies for ' + pkg_name +
                              ' configuration ...')
                    ## do nothing else but check dependencies
                    cmd = [sys.executable, os.path.join(pkg_dir, 'setup.py'),
                           'dependencies',
                           '--sublevel=' + str(self.sublevel + 1)]
                    if self.system_install:
                        cmd.append('--system-install')
                    if self.show:
                        cmd.append('--show')
                    if self.show_subpackages:
                        cmd.append('--show-subpackages')

                    if not os.path.exists(options.target_build_dir):
                        mkdir(options.target_build_dir)
                    p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         shell=shell)
                    log = open(logfile, 'a')
                    log.write(pkg_name.upper() + ':\n')
                    if INTERLEAVED_OUTPUT:
                        out = ''
                        o_q = Queue()
                        o = Thread(target=enqueue_output, args=(p.stdout, o_q))
                        e_q = Queue()
                        e = Thread(target=enqueue_output, args=(p.stderr, e_q))
                        o.start()
                        e.start()
                        while p.poll() is None:
                            try:
                                line = o_q.get_nowait()
                                out += line
                                log.write(line)
                                if not self.log_only:
                                    print(line),
                            except Exception:  # pylint: disable=W0703
                                pass
                            try:
                                line = e_q.get_nowait()
                                log.write(line)
                                if not self.log_only:
                                    print(line),
                            except Exception:  # pylint: disable=W0703
                                pass
                        o.join()
                        e.join()
                    else:
                        out, err = p.communicate()
                        log.write(out)
                        log.write(err)
                        if not self.log_only:
                            print(out),
                            print(err),
                                    
                    log.write('\n\n')
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
                    '''
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

        ## FIXME
        if self.sublevel == 0:
            env_old = self.distribution.environment
            locally = not self.system_install
            env = configure_system(self.requirements, self.distribution.version,
                                   install=(not self.show), locally=locally)
            if self.show:
                print(self.distribution.metadata.name + ' ' +
                      token + ', '.join(set([' '.join(d.split())
                                             for d in deps_list])))
            else:
                self.distribution.environment = dict(list(env_old.items()) +
                                                     list(env.items()))
        else:  ## sysdevel subpackage, collect via stdout (see above)
            print(token + ', '.join(deps_list))
        self.ran = True
