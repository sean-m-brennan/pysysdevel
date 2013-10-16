from __future__ import absolute_import

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

try:
    from numpy.distutils.command.install_data import install_data as old_data
except:
    from distutils.command.install_data import install_data as old_data

from . import util


class install_data(old_data):
    def initialize_options(self):
        old_data.initialize_options(self)
        self.data_dirs = self.distribution.data_dirs
        if self.data_files is None:
            self.data_files = []

 
    def finalize_options(self):
        install = self.get_finalized_command('install')
        if not hasattr(install, 'install_data'):
            if install.prefix is None:
                self.data_install_dir = os.path.join(install.install_base, 'share')
            else:
                self.data_install_dir = os.path.join(install.prefix, 'share')
        else:
            self.data_install_dir = install.install_data
        old_data.finalize_options(self)


    def run (self):
        old_data.run(self)
        util.mkdir(self.data_install_dir)
        if (not hasattr(self.distribution, 'using_py2exe') or \
                not self.distribution.using_py2exe) and self.data_dirs:
           for tpl in self.data_dirs:
                target = os.path.join(self.data_install_dir, tpl[0])
                for d in tpl[1]:
                    util.copy_tree(d, target, excludes=['.svn*', 'CVS*',
                                                        'Makefile*'])
