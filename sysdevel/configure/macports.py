
import os
import platform
import sys

from sysdevel.util import *
from sysdevel.configuration import config

class configuration(config):
    """
    Find/fetch MacPorts
    """
    def __init__(self):
        config.__init__(self, debug=False)
        self.ports_found = False


    def is_installed(self, environ, version):
        self.found = system_uses_macports()
        if self.found:
            self.ports_found = os.path.exists(python_executable())
            if self.ports_found and \
                    not sys.executable in python_sys_executables():
                switch_python()
        return self.found and self.ports_found


    def install(self, environ, version, locally=True):
        if not 'darwin' in platform.system().lower():
            return
        mkdir(target_build_dir)
        log = open(os.path.join(target_build_dir, 'macports_setup.log'), 'w')
        if not self.found:
            if version is None:
                version = '2.1.3'
            python_version = '26'
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
        if not self.ports_found:
            admin_check_call(['port', 'install', 'python' + python_version,
                              'python_select'], stdout=log, stderr=log)
            admin_check_call(['port', 'select', '--set', 'python',
                              'python' + python_version],
                             stdout=log, stderr=log)
            admin_check_call(['port', 'install',
                              'py' + python_version + '-numpy'],
                             stdout=log, stderr=log)
            admin_check_call(['port', 'install',
                              'py' + python_version + '-py2app-devel'],
                             stdout=log, stderr=log)
        log.close()
        if not self.is_installed(environ, verson):
            raise Exception("Macports installation failed.")



def python_executable():
    return os.path.join(macports_prefix(), 'bin', 'python')


def python_sys_executables():
    return glob.glob(os.path.join(macports_prefix(), 'bin', 'python*'))


def switch_python():
    """Magically switch to macports python"""
    env = os.environ.copy()
    env['PATH'] = [os.path.join(macports_prefix(), 'bin'),
                   os.path.join(macports_prefix(), 'sbin'),] + [env.get('PATH', '')]
    sys.stdout.write('Switching to MacPorts Python ')
    if VERBOSE:
        sys.stdout.write(python_executable() + ' ' + ' '.join(sys.argv))
    sys.stdout.write('\n\n')
    sys.stdout.flush()
    os.execve(python_executable(), [python_executable()] + sys.argv, env)
