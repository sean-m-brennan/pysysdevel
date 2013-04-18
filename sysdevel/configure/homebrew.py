"""
Find or fetch Homebrew
"""

import subprocess
import platform
import sys
import os
import glob

from sysdevel.util import *

environment = dict()
homebrew_found = False
DEBUG = False

repositories = ['Homebrew/homebrew-dupes',
                'Homebrew/homebrew-science',
                #'Homebrew/homebrew-versions',
                'samueljohn/homebrew-python', ]

def null():
    pass


def is_installed(environ, version):
    global homebrew_found
    homebrew_found = system_uses_homebrew()
    if homebrew_found and \
            not sys.executable in python_sys_executables():
        switch_python()
    return homebrew_found


def install(environ, version, locally=True):
    if not 'darwin' in platform.system().lower():
        return
    if not homebrew_found:
        check_call('ruby -e "$(curl -fsSL https://raw.github.com/mxcl/homebrew/go)"')
        check_call(['brew', 'doctor'])
        check_call(['brew', 'install', 'git'])
        for repo in repositories:
            check_call(['brew', 'tap', repo])
        check_call(['brew', 'install', 'python', '--universal',
                               '--framework'])
        check_call([pip_executable(), 'install', 'numpy'])
        check_call([pip_executable(), 'install', 'distribute'])
        check_call(['brew', 'install', 'sip'])
        check_call(['brew', 'install', 'pyqt'])
        check_call([pip_executable(), 'install', 'py2app'])
        switch_python()


def pip_executable():
    return os.path.join(homebrew_prefix(), 'bin', 'pip')


def python_executable():
    return os.path.join(homebrew_prefix(), 'bin', 'python')


def python_sys_executables():
    return glob.glob(
        os.path.join(homebrew_prefix(), 'Cellar', 'python', '*',
                     'Frameworks', 'Python.framework', 'Versions', '*',
                     'Resources', 'Python.app', 'Contents', 'MacOS', 'Python'))


def switch_python():
    """Magically switch to homebrew python"""
    env = os.environ.copy()
    env['PATH'] = os.path.join(homebrew_prefix(), 'share', 'python') + \
        os.pathsep + os.path.join(homebrew_prefix(), 'bin') + \
        os.pathsep + env.get('PATH', [])
    sys.stdout.write('Switching to Homebrew Python ')
    if VERBOSE:
        sys.stdout.write(python_executable() + ' ' + ' '.join(sys.argv))
    sys.stdout.write('\n\n')
    sys.stdout.flush()
    os.execve(python_executable(), [python_executable()] + sys.argv, env)
