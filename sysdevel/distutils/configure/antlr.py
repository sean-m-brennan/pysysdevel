
import os
import sys
import shutil

from ..prerequisites import programfiles_directories, find_file, ConfigError
from ..fetching import fetch, unarchive
from ..configuration import prog_config
from .. import options

class configuration(prog_config):
    """
    Find/install ANTLR (supports v2, v3, or v4)
    """
    def __init__(self):
        prog_config.__init__(self, 'antlr', dependencies=['java'], debug=False)


    def is_installed(self, environ, version=None):
        if version is None:
            version = '3.1.2'
        options.set_debug(self.debug)
        limit = False
        antlr_root = None
        if 'ANTLR' in environ and environ['ANTLR']:
            antlr_root = environ['ANTLR']
            limit = True

        classpaths = []
        if not limit:
            try:
                pathlist = environ['CLASSPATH'].split(os.pathsep)
                for path in pathlist:
                    classpaths.append(os.path.dirname(path))
            except KeyError:
                pass
            try:
                antlr_root = os.environ['ANTLR_ROOT']
            except KeyError:
                pass
            for d in programfiles_directories():
                classpaths.append(os.path.join(d, 'ANTLR', 'lib'))

        try:
            jarfile = find_file('antlr*' + version[0] + '*.jar',
                                ['/usr/share/java', '/usr/local/share/java',
                                 '/opt/local/share/java',
                                 os.path.join(environ['JAVA_HOME'], 'lib'),
                                 antlr_root,] + classpaths)
            self.environment['ANTLR'] = [environ['JAVA'],
                                         "-classpath", os.path.abspath(jarfile),
                                         "org.antlr.Tool",]
            self.found = True
        except ConfigError:
            if self.debug:
                print(sys.exc_info()[1])
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '3.1.2'
            website = 'http://www.antlr' + str(version[0]) + '.org/download/'
            src_dir = 'antlr-' + str(version)
            archive = src_dir + '.tar.gz'
            fetch(website, archive, archive)
            unarchive( archive, src_dir)
            jarfile = os.path.join(options.target_build_dir, src_dir + '.jar')
            if locally:
                shutil.copy(os.path.join(options.target_build_dir, src_dir,
                                         'lib', src_dir + '.jar'), jarfile)
            else:
                jarfile = os.path.join(environ['JAVA_HOME'], 'lib',
                                       src_dir + '.jar')
                shutil.copy(os.path.join(options.target_build_dir, src_dir,
                                         'lib', src_dir + '.jar'), jarfile)
            self.environment['ANTLR'] = [environ['JAVA'],
                                         "-classpath", os.path.abspath(jarfile),
                                         "org.antlr.Tool",]
