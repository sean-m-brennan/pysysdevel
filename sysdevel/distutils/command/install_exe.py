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
'install_data' command for installing shared libraries and executables
"""

import os
import struct

from distutils.command import install_lib
from distutils.util import change_root, convert_path


class install_exe(install_lib.install_lib):
    def run (self):
        '''
        Also install native executables
        '''
        install_lib.install_lib.run(self)

        build_exe = self.get_finalized_command('build_exe')
        install = self.get_finalized_command('install')

        if install.prefix is None:
            target_dir = os.path.join(install.install_base, 'bin')
        else:
            target_dir = os.path.join(install.prefix, 'bin')
        self.mkpath(target_dir)
        for exe in build_exe.install_executables:
            source = os.path.join(build_exe.build_temp, exe)
            self.copy_file(source, target_dir)
