
import os

from sysdevel.util import *
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install mod_pywebsocket
    """
    def __init__(self):
        py_config.__init__(self, 'mod_pywebsocket', '0.7.6', debug=False)


    def is_installed(self, environ, version):
        try:
            import mod_pywebsocket
            self.found = True
        except Exception, e:
            if self.debug:
                print e
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            website = 'http://pywebsocket.googlecode.com/files/'
            if version is None:
                version = self.version
            src_dir = 'pywebsocket-' + str(version)
            archive = 'mod_' + src_dir + '.tar.gz'
            pkg_dir = os.path.join(src_dir, 'src')
            install_pypkg(src_dir, website, archive,
                          src_dir=pkg_dir, locally=locally)
            if not self.is_installed(environ, version):
                raise Exception('pywebsocket installation failed.')
