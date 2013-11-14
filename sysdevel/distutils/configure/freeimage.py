
from ..prerequisites import autotools_install, global_install
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install FreeImage
    """
    def __init__(self):
        lib_config.__init__(self, "freeimage", "FreeImage.h", debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '3.15.4'
            website = ('http://downloads.sourceforge.net/project/freeimage/',
                       'Source%20Distribution/' + str(version) +'/')
            if locally or 'windows' in platform.system().lower():
                src_dir = 'FreeImage'
                archive = src_dir + str(version).replace('.', '') + '.zip'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('FreeImage', website,
                               brew='freeimage', port='freeimage-devel',
                               deb='libfreeimage-dev', rpm='freeimage-devel')
            if not self.is_installed(environ, version):
                raise Exception('FreeImage installation failed.')
