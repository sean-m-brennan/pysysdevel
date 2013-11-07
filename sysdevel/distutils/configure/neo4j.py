
import struct
import platform
import os

from ..prerequisites import *
from ..configuration import prog_config

class configuration(prog_config):
    """
    Find/install Neo4j
    """
    def __init__(self):
        prog_config.__init__(self, 'neo4j',
                             dependencies=['java'], debug=False)


    def is_installed(self, environ, version):
        if version is None:
            version = '1.9.4'
        set_debug(self.debug)
        try:
            local_dir = os.path.join(target_build_dir, 'neo4j-*', 'bin')
            self.environment['NEO4J'] = find_program('neo4j', [local_dir])
            self.found = True
        except Exception as e:
            if self.debug:
                print(e)
        return self.found



    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '1.9.4'
            website = 'http://dist.neo4j.org/'
            src_dir = 'neo4j-community-' + str(version)
            archive = src_dir + '-unix.tar.gz'
            if 'windows' in platform.system().lower() or \
               (not locally and system_uses_homebrew()):
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
                fetch(website, archive, archive)
                unarchive(archive, src_dir)
                local_dir = os.path.join(target_build_dir, src_dir, 'bin')
                admin_check_call([os.path.join(local_dir, 'neo4j'), 'install'])
            else:
                fetch(website, archive, archive)
                unarchive(archive, src_dir)
                local_dir = os.path.join(target_build_dir, src_dir, 'bin')
                self.environment['NEO4J'] = [os.path.join(local_dir, 'neo4j'),
                                             'start']
