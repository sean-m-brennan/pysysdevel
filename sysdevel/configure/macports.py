"""
Find or fetch MacPorts
"""

import platform

from sysdevel.util import *

environment = dict()
macports_found = False
DEBUG = False


def null():
    pass


def is_installed(environ, version):
    global macports_found
    macports_found = system_uses_macports()
    return macports_found


def install(environ, version, locally=True):
    if not 'darwin' in platform.system().lower():
        return
    if not macports_found:
        if version is None:
            version = '2.1.3'
        website = ('https://distfiles.macports.org/MacPorts/',)
        src_dir = 'MacPorts-' + str(version)
        archive = src_dir + '.tar.gz'
        autotools_install(environ, website, archive, src_dir, False)
        patch_file('/opt/local/share/macports/Tcl/port1.0/portconfigure.tcl',
                   'default configure.ldflags',
                   '{-L${prefix}/lib}',
                   '{"-L${prefix}/lib -Xlinker -headerpad_max_install_names"}')
        patch_file('/opt/local/etc/macports/macports.conf',
                   'build_arch  i386', '#', '')
        admin_check_call(['port', 'install', 'python26', 'python_select'])
        admin_check_call(['port', 'select', '--set', 'python', 'python26'])
        admin_check_call(['port', 'install', 'py26-numpy'])
