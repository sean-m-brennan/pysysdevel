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
'test' command for building/running unit tests,
 supports python, fortran, and c/c++
"""

import os
import sys
from distutils.core import Command
from distutils import log

from .extensions import FortranUnitTest, CUnitTest, CppUnitTest
from .recur import process_subpackages
from . import util


class test(Command):
    description = "unit testing"

    user_options = []

    def initialize_options(self):
        self.tests = []

    def finalize_options(self):
        if not self.tests: 
            self.tests = self.distribution.tests


    def _get_python_tests(self):
        pytests = []
        if self.tests:
            for pkg, tests in self.tests:
                pkgtests = []
                for unit in tests:
                    if util.is_string(unit):
                        pkgtests.append(unit)
                if len(pkgtests) > 0:
                    pytests.append((pkg, pkgtests))
        return pytests

    def _has_python_tests(self):
        return len(self._get_python_tests()) > 0


    def _get_fortran_tests(self):
        ftests = []
        if self.tests:
            for pkg, tests in self.tests:
                pkgtests = []
                for unit in tests:
                    if isinstance(unit, FortranUnitTest):
                        pkgtests.append(unit)
                if len(pkgtests) > 0:
                    ftests.append((pkg, pkgtests))
        return ftests

    def _has_fortran_tests(self):
        return len(self._get_fortran_tests()) > 0


    def _get_c_tests(self):
        ctests = []
        if self.tests:
            for pkg, tests in self.tests:
                pkgtests = []
                for unit in tests:
                    if isinstance(unit, CUnitTest):
                        pkgtests.append(unit)
                if len(pkgtests) > 0:
                    ctests.append((pkg, pkgtests))
        return ctests

    def _has_c_tests(self):
        return len(self._get_c_tests()) > 0


    def _get_cpp_tests(self):
        cpptests = []
        if self.tests:
            for pkg, tests in self.tests:
                pkgtests = []
                for unit in tests:
                    if isinstance(unit, CppUnitTest):
                        pkgtests.append(unit)
                if len(pkgtests) > 0:
                    cpptests.append((pkg, pkgtests))
        return cpptests

    def _has_cpp_tests(self):
        return len(self._get_cpp_tests()) > 0


    def _get_js_tests(self):
        jstests = []
        if self.tests:
            for pkg, tests in self.tests:
                pkgtests = []
                for unit in tests:
                    if util.is_string(unit) and unit.endswith('.html'):
                        pkgtests.append(unit)
                if len(pkgtests) > 0:
                    jstests.append((pkg, pkgtests))
        return jstests

    def _has_js_tests(self):
        return len(self._get_js_tests()) > 0


    def run(self):
        failed = False
        if self.distribution.subpackages != None:
            for idx in range(len(sys.argv)):
                if 'setup.py' in sys.argv[idx]:
                    break
            argv = list(sys.argv[idx+1:])
            build = self.get_finalized_command('build')
            failed = process_subpackages(build.distribution.parallel_build,
                                         'test', build.build_base,
                                         self.distribution.subpackages,
                                         argv, False)

        ## PYTHON
        if self._has_python_tests():
            self.run_command('build')
            build = self.get_finalized_command('build')
            build_dir = build.build_base
            environ = self.distribution.environment

            pkg_dirs = [build_dir, build.build_lib,
                        os.path.join(build_dir, 'python')]
            lib_dirs = [build.build_temp]
            try:
                lib_dirs += environ['PATH']
                # FIXME need boost, etc dlls for windows
            except:
                pass
            try:
                lib_dirs.append(os.path.join(environ['MINGW_DIR'], 'bin'))
                lib_dirs.append(os.path.join(environ['MSYS_DIR'], 'bin'))
                lib_dirs.append(os.path.join(environ['MSYS_DIR'], 'lib'))
            except:
                pass
            postfix = '.'.join(build.build_temp.split('.')[1:])        

            for pkg, units in self._get_python_tests():
                test_dir = os.path.join(build_dir, 'test_' + pkg)
                if not os.path.exists(test_dir):
                    util.copy_tree('test', test_dir, excludes=['.svn*', 'CVS*'])
                f = open(os.path.join(test_dir, '__init__.py'), 'w')
                f.write("__all__ = ['" +
                        "', '".join(units) + "']\n")
                f.close()
                outfile = os.path.join(build_dir, 'test_' + pkg + '.py')
                util.create_testscript('test_' + pkg, units, outfile, pkg_dirs)
                wrap = util.create_test_wrapper(outfile, build_dir, lib_dirs)
                log.info('Python unit tests for ' + pkg)
                try:
                    util.check_call([wrap])
                except Exception:
                    failed = True
                    e = sys.exc_info()[1]
                    print(e)

        ## FORTRAN
        if self._has_fortran_tests():
            from .configure import fruit
            env = dict()
            if not fruit.is_installed(env, None):
                fruit.install(env, None)
            fortran_unittest_framework = [
                os.path.join(env['FRUIT_SOURCE_DIR'], src)
                for src in env['FRUIT_SOURCE_FILES']]

            orig_exes = self.distribution.native_executables

            build = self.get_finalized_command('build')
            lib_dir = build.build_temp
            for pkg, units in self._get_fortran_tests():
                for unit in units:
                    unit.sources = fortran_unittest_framework + unit.sources + \
                        util.create_fruit_driver(unit.name, unit.sources[0])
                    unit.library_dirs.append(lib_dir)
                    self.distribution.native_executables.append(unit)

            ## build w/ distutils thru backdoor
            cmd_obj = self.get_command_obj('build_exe')
            cmd_obj.ensure_finalized()
            cmd_obj.run()
            self.distribution.native_executables = orig_exes

            for pkg, units in self._get_fortran_tests():
                log.info('Fortran unit tests for ' + pkg)
                for unit in units:
                    try:
                        util.check_call([os.path.join(lib_dir, unit.name)])
                    except Exception:
                        failed = True
                        e = sys.exc_info()[1]
                        print(e)

        ## C
        if self._has_c_tests():
            sys.std_err.write("C unit testing is untested!") #FIXME

            from .configure import cunit
            env = dict()
            if not cunit.is_installed(env, None):
                cunit.install(env, None)

            orig_exes = self.distribution.native_executables

            build = self.get_finalized_command('build')
            lib_dir = build.build_temp
            for pkg, units in self._get_c_tests():
                for unit in units:
                    unit.sources += util.create_cunit_driver(unit.name,
                                                             unit.sources[0])
                    unit.include_dirs.append(env['CUNIT_INCLUDE_DIR'])
                    unit.libraries.append(env['CUNIT_LIBRARIES'])
                    unit.library_dirs.append(env['CUNIT_LIB_DIR'])
                    self.distribution.native_executables.append(unit)

            ## build w/ distutils thru backdoor
            cmd_obj = self.get_command_obj('build_exe')
            cmd_obj.ensure_finalized()
            cmd_obj.run()
            self.distribution.native_executables = orig_exes

            for pkg, units in self._get_c_tests():
                log.info('C unit tests for ' + pkg)
                for unit in units:
                    try:
                        util.check_call([os.path.join(lib_dir, unit.name)])
                    except Exception:
                        failed = True
                        e = sys.exc_info()[1]
                        print(e)

        ## C++
        if self._has_cpp_tests():
            sys.std_err.write("C++ unit testing is untested!") #FIXME

            from .configure import cppunit
            env = dict()
            if not cppunit.is_installed(env, None):
                cppunit.install(env, None)

            orig_exes = self.distribution.native_executables

            build = self.get_finalized_command('build')
            lib_dir = build.build_temp
            for pkg, units in self._get_cpp_tests():
                for unit in units:
                    unit.sources += util.create_cppunit_driver(unit.name)
                    unit.include_dirs.append(env['CPPUNIT_INCLUDE_DIR'])
                    unit.libraries.append(env['CPPUNIT_LIBRARIES'])
                    unit.library_dirs.append(env['CPPUNIT_LIB_DIR'])
                    self.distribution.native_executables.append(unit)

            ## build w/ distutils thru backdoor
            cmd_obj = self.get_command_obj('build_exe')
            cmd_obj.ensure_finalized()
            cmd_obj.run()
            self.distribution.native_executables = orig_exes

            for pkg, units in self._get_cpp_tests():
                log.info('C++ unit tests for ' + pkg)
                for unit in units:
                    try:
                        util.check_call([os.path.join(lib_dir, unit.name)])
                    except Exception:
                        failed = True
                        e = sys.exc_info()[1]
                        print(e)

        ## Javascript
        if self._has_js_tests():
            sys.std_err.write("Javascript unit testing is untested!") #FIXME

            from .configure import qunitsuite
            env = dict()
            if not qunitsuite.is_installed(env, None):
                qunitsuite.install(env, None)

            for pkg, units in self._get_js_tests():
                for unit in units:
                   suite = qunitsuite.QUnitSuite(unit)
                   result = unittest.TextTestRunner(verbosity=2).run(suite)
                   ## FIXME is this output needed?
                   if len(result.errors) > 0:
                       failed = true
                       for error in result.errors:
                           print(error[1])
                   if len(result.failures) > 0:
                       failed = true
                       for failure in result.failures:
                           print(failure[1])

        if failed:
            sys.exit(1)
