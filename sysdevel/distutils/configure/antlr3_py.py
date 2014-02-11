
from ..prerequisites import install_pypkg
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install ANTLR3 Python runtime
    """
    def __init__(self):
        py_config.__init__(self, 'antlr3', '3.1.3', debug=False)


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            website = 'http://www.antlr3.org/download/Python/'
            if version is None:
                version = self.version
            src_dir = 'antlr_python_runtime-' + str(version)
            archive = src_dir + '.tar.gz' 
            install_pypkg(src_dir, website, archive, locally=locally)
            if not self.is_installed(environ, version, strict):
                raise Exception('ANTLR-Python runtime installation failed.')
