
import sys

from ..prerequisites import compare_versions
from ..fetching import fetch, unarchive
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install Python image library
    """
    def __init__(self):
        py_config.__init__(self, 'PIL', '1.1.7', debug=False)


    def is_installed(self, environ, version=None, strict=False):
        try:
            import PIL.Image
            ver = PIL.Image.VERSION
            not_ok = (compare_versions(ver, version) == -1)
            if strict:
                not_ok = (compare_versions(ver, version) != 0)
            if not_ok:
                if self.debug:
                    print('Wrong version of ' + self.pkg + ': ' +
                          str(ver) + ' vs ' + str(version))
                return self.found
            self.found = True
        except ImportError:
            if self.debug:
                print(sys.exc_info()[1])
        return self.found


    def download(self, environ, version, strict=False):
        website = 'http://effbot.org/downloads/'
        if version is None:
            version = self.version
        src_dir = 'Imaging-' + str(version)
        archive = src_dir + '.tar.gz'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir
