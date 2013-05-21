"""
Facilitates pulling SCM repositories outside of the normal dependency chain.
"""


import os
import platform
import subprocess
import sys
import time

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



def git_pull_sparse(submodule, includes, excludes):
    """
    Takes a tuple, consisting of project name, repo location,
    and optional revision number,
    plus a list of directories for sparse checkout.
    """
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
        for ex in excludes:
            sparse.write('!' + ex + '/\n')
        sparse.write('*\n')  ## all files
        for incl in includes:
            sparse.write(incl + '/\n')
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
