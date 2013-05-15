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

import util


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
