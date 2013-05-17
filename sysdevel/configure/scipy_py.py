
from sysdevel.util import *
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install SciPy
    """
    def __init__(self):
        py_config.__init__(self, 'scipy', '0.11.0',
                           dependencies=['gfortran'], debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = self.version
            website = 'http://downloads.sourceforge.net/' + \
                'project/scipy/scipy/' + version + '/'
            src_dir = 'scipy-' + str(version)
            archive = src_dir + '.tar.gz' 
            install_pypkg(src_dir, website, archive, locally=locally)
                           #extra_args=['config_fc', '--fcompiler=gnu95'])
           if not self.is_installed(environ, version):
                raise Exception('SciPy installation failed.')
