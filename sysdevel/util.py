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
Utilities for handling 2and3, and miscellany
"""

import os
import sys
import platform
import subprocess


def u(x):
    if sys.version < '3':
        import codecs
        return codecs.unicode_escape_decode(x)[0]
    else:
        return x


def is_string(item):
    try:
        return isinstance(item, basestring)
    except NameError:
        return isinstance(item, str)


def uniquify(seq, id_fctn=None):
    if id_fctn is None:
        id_fctn = lambda(x): x
    result = []
    for item in seq:
        marker = id_fctn(item)
        if marker not in result:
            result.append(item)
    return result


def flatten(seq):
    result = []
    for elt in seq:
        if hasattr(elt, '__iter__') and not is_string(elt):
            result.extend(flatten(elt))
        else:
            result.append(elt)
    return result



def rcs_revision(rcs_type=None):
    if rcs_type is None:
        if os.path.exists('.git'):
            rcs_type = 'git'
        elif os.path.exists('.hg'):
            rcs_type = 'hg'
        elif os.path.exists('.svn'):
            rcs_type = 'svn'
        elif os.path.exists('CVS'):
            raise Exception('Unsupported Revision Control System.')
        else:  # tarball install
            return None

    if rcs_type.lower() == 'git':
        cmd_line = ['git', 'rev-list', 'HEAD']
    elif rcs_type.lower() == 'hg' or rcs_type.lower() == 'mercurial':
        cmd_line = ['hg', 'log', '-r', 'tip',
                    '--template "{latesttag}.{latesttagdistance}"']
    elif rcs_type.lower() == 'svn' or rcs_type.lower() == 'subversion':
        cmd_line = ['svnversion']
    else:
        raise Exception('Unknown Revision Control System.')

    shell = False
    if 'windows' in platform.system().lower():
        shell = True
    p = subprocess.Popen(cmd_line, stdout=subprocess.PIPE, shell=shell)
    out = p.communicate()[0].strip()
    if p.wait() != 0:
        raise Exception('Failed to get ' + rcs_type + ' version.')
    if rcs_type.lower() == 'git':
        return len(out.splitlines())
    elif rcs_type.lower() == 'hg' or rcs_type.lower() == 'mercurial':
        return int(out, 10)
    elif rcs_type.lower() == 'svn' or rcs_type.lower() == 'subversion':
        end = out.find('M')
        if end < 0:
            end = len(out)
        return int(out[out.find(':')+1:end], 10)
    else:
        return 0
