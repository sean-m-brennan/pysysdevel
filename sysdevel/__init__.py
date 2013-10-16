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
sysdevel package

The sysdevel package facilitates multi-model simulation development in three
areas: model coupling, data visualization, and collaboration & distribution.
"""


__all__ = ['pkg_config', 'core', 'extensions',
           'config_cc', 'config_fc', 'build_clib', 'build_doc', 'build_exe',
           'build_js', 'build_pypp_ext', 'build_py', 'build_scripts',
           'build_shlib', 'build_src', 'install_clib', 'install_data',
           'install_exe', 'install_lib', 'util', 'tree',
           'configuration', 'configure',]

import os
import sys

config_dir = os.path.join(os.path.dirname(__file__), 'configure')
support_dir = os.path.join(os.path.dirname(__file__), 'support')

using_setuptools = False  ## monkeypatching is evil

def use_setuptools():
    global using_setuptools
    if sys.version_info > (2, 5): ## setuptools is broken in at least Python 2.4
        try:
            import setuptools
            using_setuptools = True
        except:
            pass

def setuptools_in_use():
    for k in list(sys.modules.keys()):
        if k.startswith('setuptools'):
            return True
    return False

def setup_setuptools():
    ## MUST be called before distutils (get the monkeypatching out of the way)
    global using_setuptools
    if using_setuptools:
        try:
            import setuptools
            reload(setuptools.dist)  ## in case it was already loaded
            using_setuptools = True
            print("Using setuptools.")
        except:
            using_setuptools = False
            print("Setuptools is not available.")


from .configure import configure_system, FatalError

