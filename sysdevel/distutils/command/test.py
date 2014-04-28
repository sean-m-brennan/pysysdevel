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
'test' command for building/running unit tests,
 supports python, fortran, and c/c++
"""

import os
import sys
import platform
import unittest
import subprocess
from distutils.core import Command
from distutils import log

from sysdevel.distutils.configure import configure_package
from sysdevel.distutils.extensions import FortranUnitTest, CUnitTest, CppUnitTest
from sysdevel.distutils.recur import process_subpackages
from sysdevel.distutils.prerequisites import RequirementsFinder, check_call
from sysdevel.distutils.filesystem import copy_tree
from sysdevel.util import is_string
from sysdevel.distutils import options


def create_test_wrapper(pyscript, target_dir, lib_dirs):
    pyscript = os.path.basename(pyscript)
    if 'windows' in platform.system().lower():
        dst_ext = '.bat'
    else:
        dst_ext = '.sh'
    dst_file = os.path.join(target_dir, os.path.splitext(pyscript)[0] + dst_ext)
    f = open(dst_file, 'w')
    if 'windows' in platform.system().lower():
        #wexe = os.path.join(os.path.dirname(sys.executable), 'pythonw')
        exe = os.path.join(os.path.dirname(sys.executable), 'python')
        dirlist = ''
        for d in lib_dirs:
            dirlist += os.path.abspath(d) + ';' 
        f.write('@echo off\nsetlocal\n' +
                'set PATH=' + dirlist + '%PATH%\n' +
                exe + ' "%~dp0' + pyscript + '" %*')
    else:
        dirlist = ''
        for d in lib_dirs:
            dirlist += os.path.abspath(d) + ':' 
        f.write('#!/bin/bash\n\n' +
                'loc=`dirname "$0"`\n' + 
                'export LD_LIBRARY_PATH=' + dirlist + '$LD_LIBRARY_PATH\n' +
                'export DYLD_LIBRARY_PATH=' + dirlist + '$DYLD_LIBRARY_PATH\n' +
                sys.executable + ' $loc/' + pyscript + ' $@\n')
    f.close()
    os.chmod(dst_file, int('777', 8))
    return dst_file


def create_testscript(tester, units, target, pkg_dirs):
    if options.DEBUG:
        print('Creating testscript ' + target)
    f = open(target, 'w')
    f.write("#!/usr/bin/env python\n" +
            "# -*- coding: utf-8 -*-\n\n" +
            "## In case the app is not installed in the standard location\n" + 
            "import sys\n" +
            "import os\n" +
            "bases = [os.path.dirname(unicode(__file__, sys.getfilesystemencoding()))]\n"
            )
    for d in pkg_dirs:
        f.write("bases.append(r'" + d + "')\n")
    f.write("for base in bases:\n" +
            "    sys.path.insert(0, os.path.abspath(base))\n\n" +
            "##############################\n\n"
            )
    for unit in units:
        f.write("from " + tester + "." + unit + " import *\n")
    f.write("\nimport unittest\nunittest.main()\n")
    f.close()
    os.chmod(target, int('777', 8))


def create_fruit_driver(unit, srcfile):
    test_functions = ''
    i = open(srcfile, 'r')
    for line in i:
        delim = 'subroutine'
        if delim in line:
            test_functions += 'call ' + line[len(delim)+1:] + '\n'
    i.close()
    test_driver = unit + '_fruit_driver.f90'
    o = open(test_driver, 'w')
    o.write('program ' + unit + '_fruit_driver\n' +
            'use fruit\n' +
            'use ' + unit + '\n' +
            'call init_fruit\n' +
            test_functions +
            'call fruit_summary\n' +
            'end program ' + unit + '_fruit_driver\n'
            )
    o.close()
    return test_driver


def create_cunit_driver(unit, srcfile):
    i = open(srcfile, 'r')
    lines = i.readlines()
    i.close()
    setup_fctn = ''
    if not 'setUp' in lines:
        setup_fctn = 'int setUp(void) {\n  return 0;\n}\n'
    teardown_fctn = ''
    if not 'tearDown' in lines:
        teardown_fctn = 'int tearDown(void) {\n  return 0;\n}\n'
    tests = []
    for line in lines:
        start = line.find('void ')
        end = line.find('(void)')
        if start >= 0 and end > 0:
            test_name = line[start+5:end-5]
            tests.append('       (NULL == CU_add_test(pSuite, "' + test_name +
                         '", ' + test_name + ')) ')
    test_driver = unit + '_cunit_driver.cpp'
    o = open(test_driver, 'w')
    o.write('#include <CUnit/Basic.h>\n' +
            setup_fctn + teardown_fctn + 
            'int main(int argc, char* argv[]) {\n' +
            '   CU_pSuite pSuite = NULL;\n' +
            '   if (CUE_SUCCESS != CU_initialize_registry())\n' +
            '      return CU_get_error();\n' +
            '   pSuite = CU_add_suite("' + unit + '", setup, teardown);\n' +
            '   if (NULL == pSuite) {\n' +
            '      CU_cleanup_registry();\n' +
            '      return CU_get_error();\n' +
            '   }\n' +
            '   if (\n' + 
            '||\n'.join(tests) + '\n' +
            '      ) {\n' +
            '      CU_cleanup_registry();\n' +
            '      return CU_get_error();\n' +
            '   }\n' +
            '   CU_basic_set_mode(CU_BRM_VERBOSE);\n' +
            '   CU_basic_run_tests();\n' +
            '   CU_cleanup_registry();\n' +
            '   return CU_get_error();\n' +
            '}\n'
            )
    o.close()
    return test_driver


def create_cppunit_driver(unit):
    test_driver = unit + '_cppunit_driver.cpp'
    o = open(test_driver, 'w')
    o.write('#include <cppunit/CompilerOutputter.h>\n' +
            '#include <cppunit/extensions/TestFactoryRegistry.h>\n' +
            '#include <cppunit/ui/text/TestRunner.h>\n' +
            'int main(int argc, char* argv[]) {\n' +
            '  CppUnit::Test *suite = CppUnit::TestFactoryRegistry::getRegistry().makeTest();\n' +

            '  CppUnit::TextUi::TestRunner runner;\n' +
            '  runner.addTest( suite );\n' +
            '  runner.setOutputter( new CppUnit::CompilerOutputter( &runner.result(), std::cerr ) );\n' +
            '  bool wasSucessful = runner.run();\n' +
            '  return wasSucessful ? 0 : 1;\n' +
            '}\n'
            )
    o.close()
    return test_driver



# pylint: disable=W0201
class test(Command):
    description = "unit testing"

    user_options = [('sublevel=', None, 'sub-package level'),]

    def initialize_options(self):
        self.tests = []
        self.sublevel = 0

    def finalize_options(self):
        if not self.tests: 
            self.tests = self.distribution.tests
        self.sublevel = int(self.sublevel)


    def _get_python_tests(self):
        pytests = []
        if self.tests:
            for pkg, tests in self.tests:
                pkgtests = []
                for unit in tests:
                    if is_string(unit):
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
                    if is_string(unit) and unit.endswith('.html'):
                        pkgtests.append(unit)
                if len(pkgtests) > 0:
                    jstests.append((pkg, pkgtests))
        return jstests

    def _has_js_tests(self):
        return len(self._get_js_tests()) > 0


    def run(self):
        failed = False
        build = self.get_finalized_command('build')
        if self.sublevel == 0 and not build.ran:
            self.run_command('build')

        if self.distribution.subpackages != None:
            subs = []
            for (pkg_name, pkg_dir) in self.distribution.subpackages:
                rf = RequirementsFinder(os.path.join(pkg_dir, 'setup.py'))
                if rf.is_sysdevel_build:
                    subs.append((pkg_name, pkg_dir))
            idx = 0
            for i in range(len(sys.argv)):
                idx = i
                if 'setup.py' in sys.argv[idx]:
                    break
            argv = list(sys.argv[idx+1:])
            for arg in sys.argv:
                if arg == 'clean' or '--sublevel' in arg:
                    argv.remove(arg)

            argv += ['--sublevel=' + str(self.sublevel + 1)]
            failed = process_subpackages(build.distribution.parallel_build,
                                         'test', build.build_base, subs,
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
                lib_dirs += environ['PATH']  ## need dlls for windows
            except KeyError:
                pass
            try:
                lib_dirs.append(os.path.join(environ['MINGW_DIR'], 'bin'))
                lib_dirs.append(os.path.join(environ['MSYS_DIR'], 'bin'))
                lib_dirs.append(os.path.join(environ['MSYS_DIR'], 'lib'))
            except KeyError:
                pass
            #postfix = '.'.join(build.build_temp.split('.')[1:])        

            for pkg, units in self._get_python_tests():
                test_dir = os.path.join(build_dir, 'test_' + pkg)
                if not os.path.exists(test_dir):
                    copy_tree('test', test_dir, excludes=['.svn*', 'CVS*'])
                f = open(os.path.join(test_dir, '__init__.py'), 'w')
                f.write("__all__ = ['" +
                        "', '".join(units) + "']\n")
                f.close()
                outfile = os.path.join(build_dir, 'test_' + pkg + '.py')
                create_testscript('test_' + pkg, units, outfile, pkg_dirs)
                wrap = create_test_wrapper(outfile, build_dir, lib_dirs)
                log.info('Python unit tests for ' + pkg)
                try:
                    check_call([wrap])
                except subprocess.CalledProcessError:
                    failed = True
                    print(sys.exc_info()[1])

        ## FORTRAN
        if self._has_fortran_tests():
            env = configure_package('fruit')
            fortran_unittest_framework = [
                os.path.join(env['FRUIT_SOURCE_DIR'], src)
                for src in env['FRUIT_SOURCE_FILES']]
            orig_exes = self.distribution.native_executables

            build = self.get_finalized_command('build')
            lib_dir = build.build_temp
            for pkg, units in self._get_fortran_tests():
                for unit in units:
                    unit.sources = fortran_unittest_framework + unit.sources + \
                        create_fruit_driver(unit.name, unit.sources[0])
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
                        check_call([os.path.join(lib_dir, unit.name)])
                    except subprocess.CalledProcessError:
                        failed = True
                        print(sys.exc_info()[1])

        ## C
        if self._has_c_tests():
            env = configure_package('cunit')
            orig_exes = self.distribution.native_executables

            build = self.get_finalized_command('build')
            lib_dir = build.build_temp
            for pkg, units in self._get_c_tests():
                for unit in units:
                    unit.sources += create_cunit_driver(unit.name,
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
                        check_call([os.path.join(lib_dir, unit.name)])
                    except subprocess.CalledProcessError:
                        failed = True
                        print(sys.exc_info()[1])

        ## C++
        if self._has_cpp_tests():
            env = configure_package('cppunit')
            orig_exes = self.distribution.native_executables

            build = self.get_finalized_command('build')
            lib_dir = build.build_temp
            for pkg, units in self._get_cpp_tests():
                for unit in units:
                    unit.sources += create_cppunit_driver(unit.name)
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
                        check_call([os.path.join(lib_dir, unit.name)])
                    except subprocess.CalledProcessError:
                        failed = True
                        print(sys.exc_info()[1])

        ## Javascript
        if self._has_js_tests():
            env = configure_package('qunitsuite')
            from qunitsuite.suite import QUnitSuite  \
                # pylint: disable=F0401,E0602
            for pkg, units in self._get_js_tests():
                for unit in units:
                    suite = QUnitSuite(unit)
                    result = unittest.TextTestRunner(verbosity=2).run(suite)
                    if len(result.errors) > 0:
                        failed = True
                        for error in result.errors:
                            print(error[1])
                    if len(result.failures) > 0:
                        failed = True
                        for failure in result.failures:
                            print(failure[1])

        if failed:
            sys.exit(1)
