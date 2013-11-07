
from ..prerequisites import *
from ..configuration import prog_config

class configuration(prog_config):
    """
    Find/install sshfs
    """
    def __init__(self):
        prog_config.__init__(self, 'sshfs', debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            website = ('https://www.eldos.com/files/sftpnetdrive2/')
            # FIXME no good Windows solution
            global_install('sshfs', website,
                           #winstaller='SftpNetDriveFree.exe',
                           brew='sshfs', port='sshfs',
                           deb='sshfs', rpm='fuse-sshfs')
            if not self.is_installed(environ, version):
                raise Exception('sshfs installation failed.')
