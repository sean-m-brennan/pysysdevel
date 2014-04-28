
import os
import sys
import platform
import glob
import subprocess

from sysdevel.distutils.prerequisites import find_program, global_install, ConfigError
from sysdevel.distutils.configuration import config
from sysdevel.distutils import options

class configuration(config):
    """
    Find/install Java
    """
    def __init__(self):
        config.__init__(self, debug=False)


    def null(self):
        self.environment['JAVA'] = None
        self.environment['JAVA_HOME'] = None
        self.environment['JAVAC'] = None
        self.environment['JAR'] = None
        self.environment['CLASSPATH'] = []


    def is_installed(self, environ, version=None, strict=False):
        options.set_debug(self.debug)
        try:
            locations = glob.glob(os.path.join('C:' + os.sep + 'OpenSCG',
                                               'openjdk*'))
            java_runtime = find_program('java', locations)
            java_compiler = find_program('javac', locations)
            jar_archiver = find_program('jar', locations)

            if not self.__check_java_version(java_runtime, [version]):
                return self.found
            classpaths = []
            try:
                _sep_ = ':'
                if 'windows' in platform.system().lower():
                    _sep_ = ';'
                pathlist = os.environ['CLASSPATH'].split(_sep_)
                for path in pathlist:
                    classpaths.append(path)
            except KeyError:
                pass
            self.found = True
        except ConfigError:
            if self.debug:
                print(sys.exc_info()[1])
            return self.found

        self.environment['JAVA'] = java_runtime
        self.environment['JAVA_HOME'] = os.path.abspath(os.path.join(
                os.path.dirname(java_runtime), '..'))
        self.environment['JAVAC'] = java_compiler
        self.environment['JAR'] = jar_archiver
        self.environment['CLASSPATH'] = classpaths
        return self.found


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if version is None:
                version = '1.6.0'
            sub = str(version).split('.')[1]
            website = 'http://www.java.com/'
            installer = None
            if 'darwin' in platform.system().lower():
                raise Exception('Java is included with OSX. What happened?')
            if 'windows' in platform.system().lower():
                website = 'http://oscg-downloads.s3.amazonaws.com/installers/'
                installer = 'oscg-openjdk6b24-1-windows-installer.exe'
            #TODO no local install
            global_install('Java', website,
                           winstaller=installer,
                           deb='openjdk-' + sub + '-jdk',
                           rpm='java-1.' + str(version) + '-openjdk-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('Java installation failed.')


    def __check_java_version(self, java_cmd, version_list):
        cmd_line = [java_cmd, '-version']
        p = subprocess.Popen(cmd_line,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        for ver in version_list:
            if ver is None:
                continue
            if not ver in out and not ver in err:
                return False
        return True
