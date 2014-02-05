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
modified 'sdist' command
"""

from .. import USING_SETUPTOOLS, setup_setuptools
setup_setuptools()

import os
import glob

# pylint: disable=W0201
try:
    from numpy.distutils.command.sdist import sdist as old_sdist
except ImportError:
    from distutils.command.sdist import sdist as old_sdist


if USING_SETUPTOOLS:
    have_setuptools = True
    try:
        # pylint: disable=F0401,W0611
        # very old versions of setuptools don't have this
        from setuptools.command import bdist_egg
    except ImportError:
        have_setuptools = False
else:
    have_setuptools = False


class sdist(old_sdist):
    def extend_filelist (self):
        self.filelist.extend(glob.glob('third_party/*'))

    def run (self):
        if have_setuptools:
            self.run_command('egg_info')
            ei_cmd = self.get_finalized_command('egg_info')
            self.filelist = ei_cmd.filelist
            self.filelist.append(os.path.join(ei_cmd.egg_info,'SOURCES.txt'))
            self.extend_filelist()
            self.check_readme()
            self.check_metadata()
            self.make_distribution()
            dist_files = getattr(self.distribution,'dist_files',[])
            for f in self.archive_files:
                data = ('sdist', '', f)
                if data not in dist_files:
                    dist_files.append(data)
        else:
            from distutils.filelist import FileList
            self.filelist = FileList()
            self.check_metadata()
            self.get_file_list()
            self.extend_filelist()
            if self.manifest_only:
                return
            self.make_distribution()
