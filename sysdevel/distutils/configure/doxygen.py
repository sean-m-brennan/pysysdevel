
from ..prerequisites import *
from ..configuration import prog_config

class configuration(prog_config):
    """
    Find/install Doxygen
    """
    def __init__(self):
        prog_config.__init__(self, 'doxygen', debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '1.8.3.1'
            website = ('http://ftp.stack.nl/pub/users/dimitri/',)
            # FIXME no local install
            global_install('Doxygen', website,
                           winstaller='doxygen-' + str(version) + '-setup.exe',
                           brew='doxygen', port='doxygen',
                           deb='doxygen', rpm='doxygen')
            if not self.is_installed(environ, version):
                raise Exception('Doxygen installation failed.')
