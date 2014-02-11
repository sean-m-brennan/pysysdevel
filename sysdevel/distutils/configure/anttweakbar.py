
import platform

from ..prerequisites import autotools_install, global_install
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install AntTweakBar
    """
    def __init__(self):
        lib_config.__init__(self, "AntTweakBar", "AntTweakBar.h", debug=False)


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if version is None:
                version = '116'
            website = ('http://downloads.sourceforge.net/project/anttweakbar/',)
            if locally or 'windows' in platform.system().lower():
                src_dir = 'AntTweakBar'
                archive = src_dir + '_' + str(version) + '.zip'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('AntTweakBar', website,
                               brew='anttweakbar', port='AntTweakBar',
                               deb='anttweakbar-dev', rpm='AntTweakBar-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('AntTweakBar installation failed.')
