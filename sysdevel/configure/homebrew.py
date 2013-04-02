"""
Find or fetch Homebrew
"""

import subprocess
import platform

from sysdevel.util import *

environment = dict()
homebrew_found = False
DEBUG = False

repositories = ['Homebrew/homebrew-versions',
                'Homebrew/homebrew-dupes',
                'samueljohn/homebrew-python', ]

def null():
    pass


def is_installed(environ, version):
    global homebrew_found
    homebrew_found = _uses_homebrew()
    return homebrew_found


def install(environ, version, locally=True):
    if not 'darwin' in platform.system().lower():
        return
    if not homebrew_found:
        subprocess.check_call('ruby -e "$(curl -fsSL https://raw.github.com/mxcl/homebrew/go)"')
        subprocess.check_call(['brew', 'doctor'])
        subprocess.check_call(['brew', 'install', 'git'])
        for repo in repositories:
            subprocess.check_call(['brew', 'tap', repo])
        subprocess.check_call(['brew', 'install', 'python26', 'numpy'])
