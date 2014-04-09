
import platform

from ..prerequisites import autotools_install_without_fetch, global_install
from ..fetching import fetch, unarchive
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install FreeImage
    """
    def __init__(self):
        lib_config.__init__(self, "freeimage", "FreeImage.h", debug=False)


    def download(self, environ, version, strict=False):
        if version is None:
            version = '3.15.4'
        website = 'http://downloads.sourceforge.net/project/freeimage/' + \
                  'Source%20Distribution/' + str(version) +'/'
        src_dir = 'FreeImage'
        archive = src_dir + str(version).replace('.', '') + '.zip'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if locally or 'windows' in platform.system().lower():
                src_dir = self.download(environ, version, strict)
                autotools_install_without_fetch(environ, src_dir, locally)
            else:
                global_install('FreeImage', None,
                               brew='freeimage', port='freeimage-devel',
                               deb='libfreeimage-dev', rpm='freeimage-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('FreeImage installation failed.')
