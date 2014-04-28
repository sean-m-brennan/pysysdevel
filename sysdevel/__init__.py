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
sysdevel package

The sysdevel package facilitates multi-model simulation development in three
areas: model coupling, data visualization, and collaboration & distribution.
"""

import os

CONFIG_DIR = os.path.realpath(os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'distutils', 'configure')))

SERVER_SUPPORT_DIR = os.path.realpath(os.path.abspath(
    os.path.dirname(__file__)))
SERVER_SUPPORT_MODULES = ['serve']

CLIENT_SUPPORT_DIR = os.path.realpath(os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'ui')))

from sysdevel.distutils.building import configure_file
