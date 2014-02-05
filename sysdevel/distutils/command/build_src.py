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
'build_src' command, adding module generation using ANTLR grammars
"""

import os
import shutil
import glob
import subprocess

# pylint: disable=W0201
try:
    from numpy.distutils.command.build_src import build_src as _build_src
except ImportError:
    from distutils.command.build_ext import build_ext as _build_src

from ..filesystem import mkdir
from ..building import configure_file
from ... import SERVER_SUPPORT_DIR, SERVER_SUPPORT_MODULES


class build_src(_build_src):
    '''
    Build python modules from ANTLR grammars or add sysdevel support files
    '''
    def initialize_options(self):
        _build_src.initialize_options(self)
        self.sysdevel_server = []
        self.antlr_modules = []

    def finalize_options(self):
        _build_src.finalize_options(self)
        self.sysdevel_server = self.distribution.sysdevel_server
        self.antlr_modules = self.distribution.antlr_modules
  

    def run(self):
        environ = self.distribution.environment

        if self.sysdevel_server:
            for target in self.sysdevel_server:
                if self.distribution.verbose:
                    print('adding sysdevel support to ' + target)
                target_dir = os.path.abspath(os.path.join(self.build_lib,
                                                          *target.split('.')))
                mkdir(target_dir)
                source_dir = SERVER_SUPPORT_DIR
                for mod in SERVER_SUPPORT_MODULES:
                    src_file = os.path.join(source_dir, mod + '.py.in')
                    if not os.path.exists(src_file):
                        src_file = src_file[:-3]
                    dst_file = os.path.join(target_dir, mod + '.py')
                    configure_file(environ, src_file, dst_file)


        if self.antlr_modules:
            here = os.getcwd()
            for grammar in self.antlr_modules:
                if self.distribution.verbose:
                    print('building antlr grammar "' + \
                        grammar.name + '" sources')
                ##TODO build in build_src, add to build_lib modules
                target = os.path.abspath(os.path.join(self.build_lib,
                                                      grammar.directory))
                mkdir(target)
                source_dir = os.path.abspath(grammar.directory)
                os.chdir(target)

                reprocess = True
                ref = os.path.join(target, grammar.name + '2Py.py')
                if os.path.exists(ref):
                    reprocess = False
                    for src in grammar.sources:
                        src_path = os.path.join(source_dir, src)
                        if os.path.getmtime(ref) < os.path.getmtime(src_path):
                            reprocess = True
                if reprocess:
                    for src in grammar.sources:
                        ## ANTLR cannot parse from a separate directory
                        shutil.copy(os.path.join(source_dir, src), '.')
                        cmd_line = list(environ['ANTLR'])
                        cmd_line.append(src)
                        status = subprocess.call(cmd_line)
                        if status != 0:
                            raise Exception("Command '" + str(cmd_line) +
                                            "' returned non-zero exit status "
                                            + str(status))
                    ## Cleanup so that it's only Python modules
                    for f in glob.glob('*.g'):
                        os.unlink(f)
                    for f in glob.glob('*.tokens'):
                        os.unlink(f)
                os.chdir(here)

        if self.distribution.has_ext_modules():
            _build_src.run(self)
