
import os
import platform

from ..prerequisites import autotools_install_without_fetch, global_install
from ..fetching import fetch, unarchive
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install liblzf
    """
    def __init__(self):
        lib_config.__init__(self, "lzf", "lzf.h", debug=False)


    def download(self, environ, version, strict=False):
        if version is None:
            version = '3.6'
        website = 'http://dist.schmorp.de/liblzf/Attic/'
        src_dir = 'liblzf-' + str(version)
        archive = src_dir + '.tar.gz'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if locally or 'windows' in platform.system().lower():
                src_dir = self.download(environ, version, strict)
                autotools_install_without_fetch(environ, src_dir, locally)
            else:
                here = os.getcwd()
                global_install('LZF', None,
                               brew=os.path.join(here, 'liblzf.rb'),
                               port='liblzf',
                               deb='liblzf-dev', rpm='liblzf-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('LZF installation failed.')
