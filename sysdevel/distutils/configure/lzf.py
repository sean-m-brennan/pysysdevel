
import os
import platform

from ..prerequisites import *
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install liblzf
    """
    def __init__(self):
        lib_config.__init__(self, "lzf", "lzf.h", debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '3.6'
            website = ('http://dist.schmorp.de/liblzf/Attic/',)
            if locally or 'windows' in platform.system().lower():
                src_dir = 'liblzf-' + str(version)
                archive = src_dir + '.tar.gz'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('LZF', website,
                               brew=os.path.join(here, 'liblzf.rb'),
                               port='liblzf',
                               deb='liblzf-dev', rpm='liblzf-devel')
            if not self.is_installed(environ, version):
                raise Exception('LZF installation failed.')
