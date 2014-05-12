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
'build_doc' command (see sub commands)
"""

from distutils.core import Command


class build_doc(Command):
    description = "build documentation (sphinx, org-mode, and/or docbook)"

    ## Order is important
    sub_commands = [('build_org',     lambda *args: True),
                    ('build_docbook', lambda *args: True),
                    ('build_sphinx',  lambda *args: True),]

    def initialize_options (self):
        pass

    def finalize_options (self):
        pass

    def run(self):
        if not self.distribution.has_documents():
            return

        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)
