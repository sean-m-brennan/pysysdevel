"""
modified 'sdist' command
"""

import os
import glob
import sys

try:
    from numpy.distutils.command.sdist import sdist as old_sdist
except ImportError, e:
    from distutils.command.sdist import sdist as old_sdist


if 'setuptools' in sys.modules:
    have_setuptools = True
    from setuptools import setup as old_setup
    # easy_install imports math, it may be picked up from cwd
    from setuptools.command import easy_install
    try:
        # very old versions of setuptools don't have this
        from setuptools.command import bdist_egg
    except ImportError:
        have_setuptools = False
else:
    from distutils.core import setup as old_setup
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
            for file in self.archive_files:
                data = ('sdist', '', file)
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
