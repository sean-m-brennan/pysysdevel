
from sysdevel.util import *
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install ffnet package
    """
    def __init__(self):
        py_config.__init__(self, 'ffnet', '0.7.1',
                           dependencies=['scipy', 'networkx'], debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = self.version
            website = 'http://prdownloads.sourceforge.net/ffnet/'
            src_dir = 'ffnet-' + str(version)
            archive = src_dir + '.tar.gz'
            install_pypkg(src_dir, website, archive, locally=locally)
            ## Inexplicable failure here
            #if not self.is_installed(environ, version):
            #    raise Exception('ffnet installation failed.')
