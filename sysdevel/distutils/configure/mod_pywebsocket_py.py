
from ..fetching import fetch, unarchive
from ..configuration import py_config

## PyPI entry includes *only* the latest version
class configuration(py_config):
    """
    Find/install mod_pywebsocket
    """
    def __init__(self):
        py_config.__init__(self, 'mod_pywebsocket', '0.7.6', debug=False)


    def download(self, environ, version, strict=False):
        website = 'http://pywebsocket.googlecode.com/files/'
        if version is None:
            version = self.version
        src_dir = 'mod_pywebsocket-' + str(version)
        archive = src_dir + '.tar.gz' 
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir
