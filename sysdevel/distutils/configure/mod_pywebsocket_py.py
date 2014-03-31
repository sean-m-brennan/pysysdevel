
from ..prerequisites import install_pypkg
from ..configuration import py_config

## PyPI entry includes *only* the latest version
class configuration(py_config):
    """
    Find/install mod_pywebsocket
    """
    def __init__(self):
        py_config.__init__(self, 'mod_pywebsocket', '0.7.6', debug=False)


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            website = 'http://pywebsocket.googlecode.com/files/'
            if version is None:
                version = self.version
            src_dir = 'mod_pywebsocket-' + str(version)
            archive = src_dir + '.tar.gz' 
            install_pypkg(src_dir, website, archive, locally=locally)
            if not self.is_installed(environ, version, strict):
                raise Exception('mod_pywebsocket installation failed.')
