
from ..prerequisites import install_pypkg
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install argparse (Should be in Python 2.7+)
    """
    def __init__(self):
        py_config.__init__(self, 'argparse', '1.2.1', debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            website = 'http://argparse.googlecode.com/files/'
            if version is None:
                version = self.version
            src_dir = 'argparse-' + version
            archive = src_dir + '.tar.gz'
            install_pypkg(src_dir, website, archive, locally=locally)
            if not self.is_installed(environ, version):
                raise Exception('argparse installation failed.')
