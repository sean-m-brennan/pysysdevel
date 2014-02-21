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
Custom Fortran compiler config
"""

try:
    import os
    import platform
    from numpy.distutils import log
    # pylint: disable=W0201
    from numpy.distutils.command.config_compiler import config_fc as old_cfg_fc

    from ...util import is_string


    class config_fc(old_cfg_fc):
        def initialize_options(self):
            old_cfg_fc.initialize_options(self)
            try:
                old_ldflags = os.environ['LDFLAGS']
            except KeyError:
                old_ldflags = ''
            if 'darwin' in platform.system().lower():
                os.environ['LDFLAGS'] = old_ldflags + ' -shared' + ' -lpython'
            else:
                os.environ['LDFLAGS'] = old_ldflags + ' -shared'


        def finalize_options(self):
            """ Perhaps not necessary? (potential OSX problem)
            from ..prerequisites import gcc_is_64bit
            if ((self.f77exec is None and self.f90exec is None) or \
                'gfortran' in self.f77exec or 'gfortran' in self.f90exec) and \
                'darwin' in platform.system().lower():
                ## Unify GCC and GFortran default outputs
                if gcc_is_64bit():
                    os.environ['FFLAGS'] = '-arch x86_64'
                    os.environ['FCFLAGS'] = '-arch x86_64'
                else:
                    os.environ['FFLAGS'] = '-arch i686'
                    os.environ['FCFLAGS'] = '-arch i686'
                """

            # the rest is *nearly* identical to that in the numpy original
            log.info('unifing config_fc, config, build_clib, build_shlib, ' +
                     'build_ext, build commands --fcompiler options')
            build_clib = self.get_finalized_command('build_clib')
            build_shlib = self.get_finalized_command('build_shlib')
            build_ext = self.get_finalized_command('build_ext')
            config = self.get_finalized_command('config')
            build = self.get_finalized_command('build')
            cmd_list = [self, config,
                        build_clib, build_shlib, build_ext, build]
            for a in ['fcompiler']:
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

except ImportError:
    from distutils.core import Command

    class config_fc(Command):
        """
        NumPy is not present, this is a dummy command.
        """
        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            pass
