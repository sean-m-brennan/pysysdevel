
import sys

from ..fetching import fetch, unarchive
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install PyGCCXML
    """
    def __init__(self):
        py_config.__init__(self, 'pygccxml', '1.0.0',
                           dependencies=['gccxml'], debug=False)


    def is_installed(self, environ, version=None, strict=False):
        try:
            import pygccxml  # pylint: disable=W0612
            self.found = True
        except ImportError:
            if self.debug:
                print(sys.exc_info()[1])
        return self.found


    def download(self, environ, version, strict=False):
        if version is None:
            version = self.version
        major = '.'.join(version.split('.')[:2])
        website = 'http://downloads.sourceforge.net/project/pygccxml/' + \
                  'pygccxml/pygccxml-' + major + '/'
        src_dir = 'pygccxml-' + str(version)
        archive = src_dir + '.zip'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir
