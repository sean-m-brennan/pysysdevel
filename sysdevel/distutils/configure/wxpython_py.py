
import os
import platform

from ..prerequisites import *
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install wxPython
    """
    def __init__(self):
        py_config.__init__(self, 'wx', '2.9.4.0', debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = self.version
            short_ver = '.'.join(version.split('.')[:2])
            py_ver = ''.join(get_python_version())
            brew_extra = ''
            win_extra = '32'
            if platform.architecture()[0] == '64bit':
                brew_extra = ' --devel'
                win_extra = '64'
            website = ('http://sourceforge.net/projects/wxpython/',
                       'files/wxPython/' + str(version) + '/')
            ## NOTE: no local install due to complex platform dependencies
        
            global_install('wxPython', website,
                           winstaller='wxPython' + short_ver + '-win' + \
                               win_extra + '-' + str(version) + '-py' + \
                               py_ver + '.exe',
                           brew='--python wxmac' + brew_extra,
                           port='py' + py_ver + '-wxpython',
                           deb='python-wxgtk python-wxtools',
                           rpm='wxPython-devel')
            if system_uses_homebrew():
                target = os.path.join(homebrew_prefix(), 'lib',
                                       'python'+'.'.join(get_python_version()),
                                       'site-packages', 'wx')
                if not os.path.exists(target):
                    os.symlink(glob.glob(os.path.join(homebrew_prefix(), 'lib',
                                                      'python2.6',
                                                      'site-packages',
                                                      'wx-*', 'wx'))[0], target)
                       
            if not self.is_installed(environ, version):
                raise Exception('wxpython installation failed.')
