
import platform

from ..prerequisites import autotools_install_without_fetch, global_install
from ..fetching import fetch, unarchive
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install AntTweakBar
    """
    def __init__(self):
        lib_config.__init__(self, "AntTweakBar", "AntTweakBar.h", debug=False)


    def download(self, environ, version, strict=False):
        if version is None:
            version = '116'
        website = 'http://downloads.sourceforge.net/project/anttweakbar/'
        src_dir = 'AntTweakBar'
        archive = src_dir + '_' + str(version) + '.zip'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if locally or 'windows' in platform.system().lower():
                self.download(environ, version, strict)
                autotools_install_without_fetch(environ, locally)
            else:
                global_install('AntTweakBar', None,
                               brew='anttweakbar', port='AntTweakBar',
                               deb='anttweakbar-dev', rpm='AntTweakBar-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('AntTweakBar installation failed.')
