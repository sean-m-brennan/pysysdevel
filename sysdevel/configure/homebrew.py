
import subprocess
import platform
import sys
import os
import glob

from sysdevel.util import *
from sysdevel.configuration import config

class configuration(config):
    """
    Find/fetch Homebrew
    """

    repositories = ['Homebrew/homebrew-dupes',
                    'Homebrew/homebrew-science',
                    #'Homebrew/homebrew-versions',
                    'samueljohn/homebrew-python', ]

    def __init__(self):
        config.__init__(self, debug=False)


    def is_installed(self, environ, version):
        self.found = system_uses_homebrew()
        if self.found and \
                not sys.executable in python_sys_executables():
            switch_python()
        return self.found


    def install(self, environ, version, locally=True):
        if not 'darwin' in platform.system().lower():
            return
        if not self.found:
            log = open(os.path.join(target_build_dir,
                                    'homebrew_build.log'), 'w')
            check_call('ruby -e "$(curl -fsSL https://raw.github.com/mxcl/homebrew/go)"',
                       stdout=log, stderr=log)
            check_call(['brew', 'doctor'], stdout=log, stderr=log)
            check_call(['brew', 'install', 'git'], stdout=log, stderr=log)
            for repo in self.repositories:
                check_call(['brew', 'tap', repo], stdout=log, stderr=log)
            check_call(['brew', 'install', 'python', '--universal',
                        '--framework'], stdout=log, stderr=log)
            check_call([pip_executable(), 'install', 'numpy'],
                       stdout=log, stderr=log)
            check_call([pip_executable(), 'install', 'distribute'],
                       stdout=log, stderr=log)
            check_call(['brew', 'install', 'sip'], stdout=log, stderr=log)
            check_call(['brew', 'install', 'pyqt'], stdout=log, stderr=log)
            check_call([pip_executable(), 'install', 'py2app'],
                       stdout=log, stderr=log)
            log.close()
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
