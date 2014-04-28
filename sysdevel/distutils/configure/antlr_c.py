
from sysdevel.distutils.prerequisites import autotools_install_without_fetch
from sysdevel.distutils.fetching import fetch, unarchive
from sysdevel.distutils.configuration import lib_config

class configuration(lib_config):
    """
    Find/install ANTLR C runtime
    """
    def __init__(self):
        lib_config.__init__(self, "antlr3c", "antlr3.h", debug=False)

    ## TODO ANTLR v2 & v4

    def download(self, environ, version, strict=False):
        if version is None:
            version = '3.1.2'
        website = 'http://www.antlr3.org/download/'
        src_dir = 'libantlr3c-' + str(version)
        archive = src_dir + '.tar.gz'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            src_dir = self.download(environ, version, strict)
            autotools_install_without_fetch(environ, src_dir, locally)
            if not self.is_installed(environ, version, strict):
                raise Exception('ANTLR-C runtime installation failed.')
