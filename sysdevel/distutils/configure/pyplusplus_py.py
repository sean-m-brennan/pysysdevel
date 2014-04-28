
import sys

from sysdevel.distutils.fetching import fetch, unarchive
from sysdevel.distutils.configuration import py_config

class configuration(py_config):
    """
    Find/install Py++
    """
    def __init__(self):
        py_config.__init__(self, 'pyplusplus', '1.0.0',
                           dependencies=['pygccxml'], debug=False)


    def is_installed(self, environ, version=None, strict=False):
        try:
            import pyplusplus  # pylint: disable=F0401,W0611,W0612
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
                  'pyplusplus/pyplusplus-' + major + '/'
        src_dir = 'Py++-' + str(version)
        archive = 'pyplusplus-' + str(version) + '.zip'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir
