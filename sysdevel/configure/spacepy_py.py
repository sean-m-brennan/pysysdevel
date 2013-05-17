
from sysdevel.util import *
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install SpacePy
    """
    def __init__(self):
        py_config.__init__(self, 'spacepy', '0.1.3',
                           dependencies=['gfortran', 'cdf', 'ffnet', 'h5py'],
                           debug=True)


    def install(self, environ, version, locally=True):
        if not self.found:
            website = 'http://downloads.sourceforge.net/project/spacepy/' + \
                'spacepy/spacepy-' + str(version) + '/'
            if version is None:
                version = self.version
            src_dir = 'spacepy-' + str(version)
            archive = src_dir + '.tar.gz' 
            install_pypkg(src_dir, website, archive, locally=locally)
                          #extra_args=['config_fc', '--fcompiler=gnu95'])
            ## FIXME silently failing
            #if not self.is_installed(environ, version):
            #    raise Exception('SpacePy installation failed.')
