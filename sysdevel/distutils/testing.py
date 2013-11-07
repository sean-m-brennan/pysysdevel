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
Utilities for unit testing
"""

import os
import sys
import platform
#DEBUG

def create_test_wrapper(pyscript, target_dir, lib_dirs):
    pyscript = os.path.basename(pyscript)
    if 'windows' in platform.system().lower():
        dst_ext = '.bat'
    else:
        dst_ext = '.sh'
    dst_file = os.path.join(target_dir, os.path.splitext(pyscript)[0] + dst_ext)
    f = open(dst_file, 'w')
    if 'windows' in platform.system().lower():
        wexe = os.path.join(os.path.dirname(sys.executable), 'pythonw')
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
    os.chmod(dst_file, 0x777)
    return dst_file


def create_testscript(tester, units, target, pkg_dirs):
    if DEBUG:
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
    os.chmod(target, 0x777)


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


