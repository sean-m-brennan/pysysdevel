"""
Find Git
"""

import os
import platform

from sysdevel.util import *

environment = dict()
git_found = False
DEBUG = False


def null():
    global environment
    environment['GIT'] = None


def is_installed(environ, version):
    global environment, git_found
    if version is None:
        version = '2.8'

    set_debug(DEBUG)
    base_dirs = [os.path.join('C:',  os.sep, 'msysgit', 'cmd')]
    try:
        base_dirs.append(os.path.join(os.environ['ProgramFiles'], 'Git', 'cmd'))
    except:
        pass
    try:
        base_dirs.append(os.path.join(environ['MSYS_DIR'], 'bin'))
    except:
        pass
    try:
        environment['GIT'] = find_program('git', base_dirs)
        git_found = True
    except Exception, e:
        if DEBUG:
            print e
    return git_found


def install(environ, version, locally=True):
    if not git_found:
        website = ('http://git-scm.com/',)
        if 'windows' in platform.system().lower():
            if version is None:
                version = '1.8.1.2-preview21130201'
                website = ('http://msysgit.googlecode.com/', 'files/')
        #FIXME no local install
        global_install('Git', website,
                       winstaller='Git-' + str(version) + '.exe',
                       brew='git', port='git-core',
                       deb='git', rpm='git')
        if not is_installed(environ, version):
            raise Exception('Git installation failed.')
