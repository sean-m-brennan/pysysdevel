
import sys
import platform

from sysdevel.util import *
from sysdevel.configuration import config

class configuration(config):
    """
    Find/fetch MacPorts
    """
    def __init__(self):
        config.__init__(self, debug=False)


    def is_installed(self, environ, version):
        self.found = system_uses_macports()
        if self.found and sys.executable != python_executable():
            switch_python()
        return self.found


    def install(self, environ, version, locally=True):
        if not 'darwin' in platform.system().lower():
            return
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
            log = open(os.path.join(target_build_dir,
                                    'macports_setup.log'), 'w')
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
            switch_python()


def port_prefix():
    return '/opt/local'

def python_executable():
    return os.path.join(port_prefix, 'bin', 'python')

def switch_python():
    """Magically switch to macports python"""
    env = sys.environ.copy()
    env['PATH'] = [os.path.join(port_prefix(), 'bin'),
                   os.path.join(port_prefix(), 'sbin'),] + env.get('PATH', [])
    sys.stdout.write('Switching to MacPorts Python ')
    if VERBOSE:
        sys.stdout.write(python_executable() + ' ' + ' '.join(sys.argv))
    sys.stdout.write('\n\n')
    sys.stdout.flush()
    os.execve(python_executable(), [python_executable()] + sys.argv, env)
