# -*- coding: utf-8 -*-
"""
'build_src' command, adding module generation using ANTLR grammars
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

import os, sys, shutil, glob, subprocess
from numpy.distutils.command.build_src import build_src as _build_src

import util


class build_src(_build_src):
    '''
    Build python modules from ANTLR grammars
    '''
    def initialize_options(self):
        _build_src.initialize_options(self)
        self.antlr_modules = []

    def finalize_options(self):
        _build_src.finalize_options(self)
        self.antlr_modules = self.distribution.antlr_modules
  

    def run(self):
        environ = self.distribution.environment

        if self.antlr_modules:
            here = os.getcwd()
            for grammar in self.antlr_modules:
                if self.distribution.verbose:
                    print 'building antlr grammar "' + \
                        grammar.name + '" sources'
                ##TODO build in build_src, add to build_lib modules
                target = os.path.abspath(os.path.join(self.build_lib,
                                                      grammar.directory))
                util.mkdir(target)
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
                        cmd_line = list(environ['ANTLR_COMMAND'])
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
        _build_src.run(self)
