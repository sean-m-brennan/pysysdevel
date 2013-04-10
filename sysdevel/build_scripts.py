# -*- coding: utf-8 -*-
"""
'build_scripts' command, adding module generation using ANTLR grammars
"""
#**************************************************************************
# 
# This material was prepared by the Los Alamos National Security, LLC 
# (LANS), under Contract DE-AC52-06NA25396 with the U.S. Department of 
# Energy (DOE). All rights in the material are reserved by DOE on behalf 
# of the Government and LANS pursuant to the contract. You are authorized 
# to use the material for Government purposes but it is not to be released 
# or distributed to the public. NEITHER THE UNITED STATES NOR THE UNITED 
# STATES DEPARTMENT OF ENERGY, NOR LOS ALAMOS NATIONAL SECURITY, LLC, NOR 
# ANY OF THEIR EMPLOYEES, MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR 
# ASSUMES ANY LEGAL LIABILITY OR RESPONSIBILITY FOR THE ACCURACY, 
# COMPLETENESS, OR USEFULNESS OF ANY INFORMATION, APPARATUS, PRODUCT, OR 
# PROCESS DISCLOSED, OR REPRESENTS THAT ITS USE WOULD NOT INFRINGE 
# PRIVATELY OWNED RIGHTS.
# 
#**************************************************************************

import os
import sys
import shutil
import glob
import subprocess
from numpy.distutils.command.build_scripts import build_scripts as _build_scripts

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
