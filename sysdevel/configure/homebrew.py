
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
        self.brews_found = False


    def is_installed(self, environ, version):
        self.found = system_uses_homebrew()
        if self.found:
            self.brews_found = os.path.exists(python_executable()) and \
                os.path.exists(pip_executable())
            if self.brews_found and \
                    not sys.executable in python_sys_executables():
                switch_python()
        return self.found and self.brews_found


    def install(self, environ, version, locally=True):
        if not 'darwin' in platform.system().lower():
            return
        mkdir(target_build_dir)
        log = open(os.path.join(target_build_dir,
                                'homebrew_build.log'), 'w')
        if not self.found:
            check_call('ruby -e "$(curl -fsSL https://raw.github.com/mxcl/homebrew/go)"',
                       stdout=log, stderr=log)
        if not self.brews_found:
            call(['brew', 'doctor'], stdout=log, stderr=log)
            call(['brew', 'install', 'git'], stdout=log, stderr=log)
            for repo in self.repositories:
                call(['brew', 'tap', repo], stdout=log, stderr=log)
            call(['brew', 'install', 'python', '--universal',
                        '--framework'], stdout=log, stderr=log)
            call([pip_executable(), 'install', 'numpy'],
                       stdout=log, stderr=log)
            call([pip_executable(), 'install', 'distribute'],
                       stdout=log, stderr=log)
            call(['brew', 'install', 'sip'], stdout=log, stderr=log)
            call(['brew', 'install', 'pyqt'], stdout=log, stderr=log)
            call([pip_executable(), 'install', 'py2app'],
                       stdout=log, stderr=log)
        log.close()
        if not self.is_installed(environ, verson):
            raise Exception("Homebrew installation failed.")


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
