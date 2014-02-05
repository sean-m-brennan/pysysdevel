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
Custom C/C++ compiler config
"""

import platform

# pylint: disable=W0201
try:
    from numpy.distutils.command.config_compiler import config_cc as old_config_cc
except ImportError:
    from distutils.core import Command as old_config_cc
from distutils import log

from ...util import is_string


# pylint: disable=W0201
class config_cc(old_config_cc):
    description = "specify C/C++ compiler information"

    user_options = [
        ('compiler=',None,"specify C/C++ compiler type"),
        ]

    def initialize_options(self):
        self.compiler = None

    def finalize_options(self):
        ## force cached compiler
        if 'windows' in platform.system().lower():
            env = self.distribution.environment
            if 'COMPILER' in env:
                self.compiler = env['COMPILER'].encode('ascii', 'ignore')

        ## *nearly* identical to that in the numpy original
        log.info('unifing config_cc, config, build_clib, build_shlib, ' +
                 'build_ext, build commands --compiler options')
        build_clib = self.get_finalized_command('build_clib')
        build_shlib = self.get_finalized_command('build_shlib')
        build_ext = self.get_finalized_command('build_ext')
        config = self.get_finalized_command('config')
        build = self.get_finalized_command('build')
        cmd_list = [self, config, build_clib, build_shlib, build_ext, build]
        for a in ['compiler']:
            l = []
            for c in cmd_list:
                v = getattr(c,a)
                if v is not None:
                    if not is_string(v): v = v.compiler_type
                    if v not in l: l.append(v)
            if not l: v1 = None
            else: v1 = l[0]
            if len(l)>1:
                log.warn('  commands have different --%s options: %s'\
                         ', using first in list as default' % (a, l))
            if v1:
                for c in cmd_list:
                    if getattr(c,a) is None: setattr(c, a, v1)
        return

    def run(self):
        # Do nothing.
        return
