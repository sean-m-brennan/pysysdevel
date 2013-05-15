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
