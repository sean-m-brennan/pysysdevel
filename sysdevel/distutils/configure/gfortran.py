
import platform

from ..prerequisites import global_install, system_uses_macports
from ..configuration import prog_config

class configuration(prog_config):
    """
    Find/fetch/install GNU Fortran
    """
    def __init__(self):
        prog_config.__init__(self, 'gfortran', debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            website = ('http://gcc.gnu.org',)
            if 'windows' in platform.system().lower():
                if version is None:
                    version = '20120426'
                website = ('http://sourceforge.net/projects/mingw/',
                           'files/Installer/mingw-get-inst/mingw-get-inst-' +
                           str(version) + '/')
            if 'darwin' in platform.system().lower() and system_uses_macports():
                raise Exception('GFortran does not appear to be installed.')
            global_install('GFortran', website,
                           winstaller='mingw-get-inst-' + str(version) + '.exe',
                           brew='gfortran ', #+ os.path.join(here, 'g77.rb'),
                           deb='gfortran', rpm='gcc-gfortran')
            if not self.is_installed(environ, version):
                raise Exception('GFortran installation failed.')
