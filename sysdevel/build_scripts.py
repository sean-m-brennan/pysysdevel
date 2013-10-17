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
'build_scripts' command, adding module generation using ANTLR grammars
"""

import os
import sys
import shutil
import glob
import subprocess

try:
    from numpy.distutils.command.build_scripts import build_scripts as _build_scripts
except:
    from distutils.command.build_scripts import build_scripts as _build_scripts

from . import util


class build_scripts(_build_scripts):
    '''
    Build python runscripts and shell wrappers
    '''
    def initialize_options(self):
        _build_scripts.initialize_options(self)
        self.create_scripts = []

    def finalize_options(self):
        _build_scripts.finalize_options(self)
        self.create_scripts = self.distribution.create_scripts
  
    def run(self):
        environ = self.distribution.environment

        util.mkdir(self.build_dir)
        if self.create_scripts:
            if not self.scripts:
                self.scripts = []
            for tpl in self.create_scripts:
                outfile = os.path.join(self.build_dir, os.path.basename(tpl[0]))
                util.create_runscript(tpl[1], tpl[2], outfile, tpl[3])
                self.scripts.append(outfile)

        if self.distribution.has_shared_libs():
            prev_list = list(self.scripts)
            for s in prev_list:
                if '.py' in s:
                    util.create_script_wrapper(s, self.build_dir)
                    self.scripts.append(s)

        if self.scripts:
            self.copy_scripts()
