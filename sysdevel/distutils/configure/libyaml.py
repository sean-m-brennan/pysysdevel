
import platform

from ..prerequisites import autotools_install_without_fetch, global_install
from ..fetching import fetch, unarchive
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install YAML library
    """
    def __init__(self):
        lib_config.__init__(self, "yaml", "yaml.h", debug=False)


    def download(self, environ, version, strict=False):
        if version is None:
            version = '0.1.4'
        #major = '.'.join(version.split('.')[:2])
        website = 'http://pyyaml.org/download/libyaml/'
        src_dir = 'yaml-' + str(version)
        archive = src_dir + '.tar.gz'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if locally or 'windows' in platform.system().lower():
                src_dir = self.download(environ, version, strict)
                autotools_install_without_fetch(environ, src_dir, locally)
            else:
                global_install('YAML', None,
                               brew='libyaml', port='libyaml',
                               deb='libyaml-dev', rpm='libyaml-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('libyaml installation failed.')
