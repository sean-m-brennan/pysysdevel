
import os
import sys
import struct
import platform

from sysdevel.distutils.prerequisites import find_program, system_uses_homebrew, global_install, admin_check_call, ConfigError
from sysdevel.distutils.fetching import fetch, unarchive
from sysdevel.distutils.configuration import prog_config
from sysdevel.distutils import options

class configuration(prog_config):
    """
    Find/install Neo4j
    """
    def __init__(self):
        prog_config.__init__(self, 'neo4j',
                             dependencies=['java'], debug=False)


    def is_installed(self, environ, version=None, strict=False):
        options.set_debug(self.debug)
        if version is None:
            version = '1.9.4'
        try:
            local_dir = os.path.join(options.target_build_dir, 'neo4j-*', 'bin')
            self.environment['NEO4J'] = find_program('neo4j', [local_dir])
            self.found = True
        except ConfigError:
            if self.debug:
                print(sys.exc_info()[1])
        return self.found


    def download(self, environ, version, strict=False):
        if version is None:
            version = '1.9.4'
        website = 'http://dist.neo4j.org/'
        src_dir = 'neo4j-community-' + str(version)
        if 'windows' in platform.system().lower():
            win_ver = version.replace('.', '_')
            win_arch = 'x32'
            if struct.calcsize('P') == 8:
                win_arch = 'x64'
            src_dir = ''
            archive = 'neo4j-community_windows-' + win_arch + \
                      '_' + win_ver + '.exe'
        else:
            archive = src_dir + '-unix.tar.gz'
        fetch(website, archive, archive)
        if not 'windows' in platform.system().lower():
            unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            src_dir = self.download(environ, version, strict)
            if 'windows' in platform.system().lower() or \
               (not locally and system_uses_homebrew()):
                website = ('http://dist.neo4j.org/',)
                win_ver = version.replace('.', '_')
                win_arch = 'x32'
                if struct.calcsize('P') == 8:
                    win_arch = 'x64'
                global_install('Neo4j', website,
                           winstaller='neo4j-community_windows-' + win_arch + \
                               '_' + win_ver + '.exe',
                           brew='neo4j',
                           ## no macports, debian or yum packages
                           )
                self.environment['NEO4J'] = ['neo4j', 'start']
            elif not locally:
                local_dir = os.path.join(options.target_build_dir,
                                         src_dir, 'bin')
                admin_check_call([os.path.join(local_dir, 'neo4j'), 'install'])
            else:
                local_dir = os.path.join(options.target_build_dir,
                                         src_dir, 'bin')
                self.environment['NEO4J'] = [os.path.join(local_dir, 'neo4j'),
                                             'start']
