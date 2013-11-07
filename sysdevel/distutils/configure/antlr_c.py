
from ..prerequisites import *
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install ANTLR C runtime
    """
    def __init__(self):
        lib_config.__init__(self, "antlr3c", "antlr3.h", debug=False)

    ## FIXME ANTLR v2 & v4

    def install(self, environ, version, locally=True):
        if not self.found:
            website = 'http://www.antlr3.org/download/'
            if version is None:
                version = '3.1.2'
            src_dir = 'libantlr3c-' + str(version)
            archive = src_dir + '.tar.gz'
            autotools_install(environ, website, archive, src_dir, locally)
            if not is_installed(environ, version):
                raise Exception('ANTLR-C runtime installation failed.')
