
from ..fetching import fetch, unarchive
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install ANTLR3 Python runtime
    """
    def __init__(self):
        py_config.__init__(self, 'antlr3', '3.1.3', debug=False)


    def download(self, environ, version, strict=False):
        if version is None:
            version = self.version
        website = 'http://www.antlr3.org/download/Python/'
        src_dir = 'antlr_python_runtime-' + str(version)
        archive = src_dir + '.tar.gz' 
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir
