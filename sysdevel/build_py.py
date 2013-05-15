"""
'build_src' command, adding module generation using ANTLR grammars
"""

import os
import sys
import shutil
import glob
import subprocess

from types import *

try:
    from numpy.distutils.command.build_py import build_py as _build_py
except:
    from distutils.command.build_py import build_py as _build_py

import util


class build_py(_build_py):
    '''
    Configure, then build python modules
    '''
    def build_module (self, module, module_file, package):
        environ = self.distribution.environment

        if type(package) is StringType:
            package = package.split('.')
        elif type(package) not in (ListType, TupleType):
            raise TypeError, \
                  "'package' must be a string (dot-separated), list, or tuple"

        # Now put the module source file into the "build" area -- this is
        # easy, we just copy it somewhere under self.build_lib (the build
        # directory for Python source).
        outfile = self.get_module_outfile(self.build_lib, package, module)
        dir = os.path.dirname(outfile)
        self.mkpath(dir)
        util.configure_file(environ, module_file, outfile)
        return (outfile, 1)
