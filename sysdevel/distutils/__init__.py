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


__all__ = ['command', 'configure',
           'building', 'configuration', 'core', 'extensions', 'fetching',
           'filesystem', 'headers', 'numpy_utils', 'pkg_config',
           'prerequisites', 'recur', 'submodules', 'tree',
           ]

import os
import sys
import glob


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
            sys.stderr.write("Using setuptools.\n")
        except:
            using_setuptools = False
            sys.stderr.write("Setuptools is not available.\n")


class _Options(object):
    default_path_prefixes = ['/usr', '/usr/local', '/opt/local',
                             ] + glob.glob('C:\\Python*\\')
    global_prefix = '/usr'

    ## immutable
    local_lib_dir = 'python'
    javascript_dir = 'javascript'
    stylesheet_dir = 'stylesheets'
    script_dir = 'scripts'
    windows_postinstall = 'postinstall.py'
    default_py2exe_library = 'library.zip'

    def __init__(self):
        ## mutable
        self._local_search_paths = []
        self._default_download_dir  = 'third_party'
        self._target_download_dir  = self._default_download_dir
        self._default_build_dir = 'build'
        self._target_build_dir = self._default_build_dir
        self._VERBOSE = False
        self._DEBUG = False

    @property
    def VERBOSE(self):
        return self._VERBOSE

    def set_verbose(self, b):
        self._VERBOSE = b

    @property
    def DEBUG(self):
        return self._DEBUG

    def set_debug(self, b):
        self._DEBUG = b

    @property
    def local_search_paths(self):
        return self._local_search_paths

    def set_local_search_paths(self, p):
        self._local_search_paths = list(p)

    def add_local_search_path(self, p):
        self._local_search_paths.append(p)

    @property
    def default_build_dir(self):
        return self._default_build_dir

    def set_build_dir(self, d):
        self._default_build_dir = d

    @property
    def download_dir(self):
        return self._target_download_dir

    @property
    def default_download_dir(self):
        return self._target_download_dir

    def set_download_dir(self, d):
        self._default_download_dir = d

    @property
    def target_build_dir(self):
        return self._target_build_dir

    def set_top_level(self, num):
        base_dir = os.path.realpath(os.path.abspath(
            os.path.sep.join(['..' for i in range(num)])))
        self._target_build_dir = os.path.join(base_dir, self.default_build_dir)
        self._target_download_dir = os.path.join(base_dir,
                                                 self.default_download_dir)
        return self._target_build_dir

options = _Options()


from .core import setup
from .extensions import *
from .configure import configure_system, FatalError
from .pkg_config import pkg_config, handle_arguments, get_options, post_setup


