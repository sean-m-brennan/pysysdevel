"""
Copyright 2013.  Los Alamos National Security, LLC. This material was
produced under U.S. Government contract DE-AC52-06NA25396 for Los
Alamos National Laboratory (LANL), which is operated by Los Alamos
National Security, LLC for the U.S. Department of Energy. The
U.S. Government has rights to use, reproduce, and distribute this
software.  NEITHER THE GOVERNMENT NOR LOS ALAMOS NATIONAL SECURITY,
LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR ASSUMES ANY LIABILITY
FOR THE USE OF THIS SOFTWARE.  If software is modified to produce
derivative works, such modified software should be clearly marked, so
as not to confuse it with the version available from LANL.

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
Utilities for finding prerequisities
"""

import os
import sys

try:
    from numpy.distutils.command.build_ext import build_ext
except:
    from distutils.command.build_ext import build_ext

import util


class build_pypp_ext(build_ext):
    '''
    Build extensions using Py++
    '''
    def run(self):
        if not self.distribution.pypp_ext_modules:
            return
        environ = self.distribution.environment

        ## Make sure that extension sources are complete.
        self.run_command('build_src')
        build = self.get_finalized_command('build')
        if self.distribution.verbose:
            print 'Creating Py++ code generators ...'

        my_build_temp = os.path.join(build.build_base, 'pypp')
        builders = []
        for pext in self.distribution.pypp_ext_modules:
            builder = os.path.basename(pext.pyppdef)[:-6]  ## assumes '.py.in'
            pext.builder = builder
            builders.append(builder)
            builder_py = os.path.join(my_build_temp, builder + '.py')
            if util.is_out_of_date(pext.pyppdef, builder_py):
                util.configure_file(environ, pext.pyppdef, builder_py)

        init = open(os.path.join(my_build_temp, '__init__.py'), 'w')
        init.write('__all__ = ' + str(builders) + '\n\n')
        init.close()
        main = open(os.path.join(my_build_temp, '__main__.py'), 'w')
        main.write('for m in __all__:\n    m.generate()\n\n')
        main.close()
        init = open(os.path.join(build.build_base, '__init__.py'), 'w')
        init.write("__all__ = ['" + os.path.basename(my_build_temp) + "']\n\n")
        init.close()

        self.extensions = []
        for pext in self.distribution.pypp_ext_modules:
            if util.is_out_of_date(os.path.join(my_build_temp,
                                                pext.builder + '.py'),
                                   pext.binding_file):
                if self.distribution.verbose:
                    print '\tfor ' + pext.name
                build_mod = my_build_temp.replace(os.sep, '.')
                full_qual = build_mod + '.' + pext.builder
                __import__(full_qual)
                generator = sys.modules[full_qual]
                pext.sources += generator.generate()
                self.extensions.append(pext)
                    
        build_ext.run(self)
