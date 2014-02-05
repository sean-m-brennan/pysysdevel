
import os
import platform
import sys
import glob

from ..prerequisites import autotools_install, admin_check_call, macports_prefix, patch_file, system_uses_macports
from ..configuration import config
from ..filesystem import mkdir
from .. import options

class configuration(config):
    """
    Find/fetch MacPorts
    """
    def __init__(self):
        config.__init__(self, debug=True)
        self.ports_found = False


    def is_installed(self, environ, version):
        options.set_debug(self.debug)
        self.found = system_uses_macports()
        if self.found:
            self.ports_found = os.path.exists(python_executable())
            exe_ok = False
            for exe in python_sys_executables():
                if exe.startswith(sys.exec_prefix):
                    exe_ok = True
                    break
            if self.ports_found and not exe_ok:
                if self.debug:
                    print(sys.exec_prefix + "/bin/python  not in  " + \
                        repr(python_sys_executables()))
                switch_python()
        return self.found and self.ports_found


    def install(self, environ, version, locally=True):
        if not 'darwin' in platform.system().lower():
            return
        mkdir(options.target_build_dir)
        log = open(os.path.join(options.target_build_dir,
                                'macports_setup.log'), 'w')
        python_version = '26'  ## Hard coded due to wxPython
        if not self.found:
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
                       'build_arch  i386', '#', '')  ## Also due to wxPython
            admin_check_call(['port', 'selfupdate'], stdout=log, stderr=log)
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
                              'py' + python_version + '-py2app'],
                             stdout=log, stderr=log)
        log.close()
        if not self.is_installed(environ, version):
            raise Exception("Macports installation failed.")



def python_executable():
    return os.path.join(macports_prefix(), 'bin', 'python')


def python_sys_executables():
    exes = glob.glob(os.path.join(macports_prefix(), 'bin', 'python*'))
    full_paths = []
    for exe in exes:
        full_paths.append(os.path.realpath(exe))
    return full_paths


def switch_python():
    """Magically switch to macports python"""
    env = os.environ.copy()
    env['PATH'] = [os.path.join(macports_prefix(), 'bin'),
                   os.path.join(macports_prefix(), 'sbin'),] + [env.get('PATH', '')]
    env['PATH'] = ':'.join(env['PATH'])
    sys.stdout.write('Switching to MacPorts Python ')
    if options.VERBOSE:
        sys.stdout.write(python_executable() + ' ' + ' '.join(sys.argv))
    sys.stdout.write('\n\n')
    sys.stdout.flush()
    os.execve(python_executable(), [python_executable()] + sys.argv, env)
