
from sysdevel.util import *
from sysdevel.configuration import lib_config

class configuration(lib_config):
    """
    Find/install YAML library
    """
    def __init__(self):
        lib_config.__init__(self, "yaml", "yaml.h", debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '0.1.4'
            major = '.'.join(version.split('.')[:2])
            website = ('http://pyyaml.org/', 'download/libyaml/')
            if locally or 'windows' in platform.system().lower():
                src_dir = 'yaml-' + str(version)
                archive = src_dir + '.tar.gz'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('YAML', website,
                               brew='libyaml', port='libyaml',
                               deb='libyaml-dev', rpm='libyaml-devel')
            if not self.is_installed(environ, version):
                raise Exception('libyaml installation failed.')
