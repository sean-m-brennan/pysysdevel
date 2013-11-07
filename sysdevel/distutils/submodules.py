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
Facilitates pulling SCM repositories outside of the normal dependency chain.
"""


import os
import platform
import subprocess
import sys
import time

def git_version():
    p = subprocess.Popen(['git', '--version'], stdout=subprocess.PIPE)
    return tuple([int(x, 10) for x in p.communicate()[0].split()[2].split('.')])


def git_pull(submodules):
    """
    Takes a list of tuples, consisting of project name, repo location,
    and optional revision number.
    """
    shell = False
    if 'windows' in platform.system().lower():
       shell = True
    here = os.path.abspath(os.getcwd())
    for sub in submodules:
        if not os.path.exists(sub[0]):
            subprocess.check_call(['git', 'clone', sub[1]], shell=shell)
            try:  ## specific revision
                os.chdir(sub[0])
                subprocess.check_call(['git', 'checkout', sub[2]], shell=shell)
            except:
                pass
        elif os.path.exists(os.path.join(sub[0], '.git')):
            ## no revision => get up-to-date
            if len(sub) < 3 or sub[2] is None:
                os.chdir(sub[0])
                subprocess.check_call(['git', 'pull'], shell=shell)
        os.chdir(here)



def git_pull_sparse(submodule, excludes):
    """
    Takes a tuple, consisting of project name, repo location,
    and optional revision number,
    plus a list of paths to exclude from sparse checkout.
    """
    ## Sparse first implemented in 1.7.0
    ## Exclusion doesn't work until 1.7.10
    if git_version() < (1, 7, 10):
        return git_pull([submodule])

    shell = False
    if 'windows' in platform.system().lower():
       shell = True
    here = os.path.abspath(os.getcwd())
    if not os.path.exists(submodule[0]):
        os.mkdir(submodule[0])
        os.chdir(submodule[0])
        subprocess.check_call(['git', 'init'], shell=shell)
        subprocess.check_call(['git', 'remote', 'add',
                               '--track', 'master', 'origin', submodule[1]],
                              shell=shell)
        subprocess.check_call("git config core.sparsecheckout true", shell=True)
        sparse = open(os.path.join('.git', 'info', 'sparse-checkout'), 'w')
        sparse.write('/*\n')  ## all files
        sparse.write('*/*\n')  ## all directories
        for ex in excludes:
            sparse.write('!' + ex + '/\n')
        sparse.close()
        subprocess.check_call(['git', 'pull'], shell=shell)
        try:  ## specific revision
            subprocess.check_call(['git', 'checkout', submodule[2]],
                                  shell=shell)
        except:
            pass
    elif os.path.exists(os.path.join(submodule[0], '.git')):
        ## no revision => get up-to-date
        if len(submodule) < 3 or submodule[2] is None:
            os.chdir(submodule[0])
            subprocess.check_call(['git', 'pull'], shell=shell)
    os.chdir(here)
