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
modified 'clean' command
"""

import os
import sys
import shutil

from distutils.command.clean import clean as old_clean

from sysdevel.distutils.recur import process_subpackages
from sysdevel.distutils.prerequisites import delete_cache, RequirementsFinder


class clean(old_clean):
    def run(self):
        # Remove .pyc, .lreg and .sibling files
        if hasattr(os, 'walk'):
            for _, _, files in os.walk('.'):
                for f in files:
                    if f.endswith('.pyc') or \
                            f.endswith('.lreg') or f.endswith('.sibling'):
                        try:
                            os.unlink(f)
                        except OSError:
                            pass

        # Remove generated directories
        build = self.get_finalized_command('build')
        build_dir = build.build_base
        if os.path.exists(build_dir):
            try:
                shutil.rmtree(build_dir, ignore_errors=True)
            except OSError:
                pass
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
            process_subpackages(build.distribution.parallel_build, 'clean',
                                build.build_base, subs, argv, False)

        # Remove user-specified generated files
        if self.distribution.generated_files != None:
            for path in self.distribution.generated_files:
                if os.path.isfile(path) or os.path.islink(path):
                    try:
                        os.unlink(path)
                    except OSError:
                        pass
                elif os.path.isdir(path):
                    try:
                        shutil.rmtree(path, ignore_errors=True)
                    except OSError:
                        pass

        # Remove sysdevel
        if os.path.exists('pysysdevel'):
            try:
                ## ignores symlinked directory
                shutil.rmtree('pysysdevel', ignore_errors=True)
            except OSError:
                pass

        old_clean.run(self)
        delete_cache()
