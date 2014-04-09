
from ..fetching import fetch, unarchive
from ..prerequisites import install_pypkg_without_fetch
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install SpacePy
    """
    def __init__(self):
        py_config.__init__(self, 'spacepy', '0.1.4',
                           dependencies=['gfortran', 'cdf', 'ffnet', 'h5py'],
                           debug=True)


    def download(self, environ, version, strict=False):
        if version is None:
            version = self.version
        website = 'http://downloads.sourceforge.net/project/spacepy/' + \
                  'spacepy/spacepy-' + str(version) + '/'
        src_dir = 'spacepy-' + str(version)
        archive = src_dir + '.tar.gz' 
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            self.download(environ, version, strict)
            install_pypkg_without_fetch(self.pkg, locally=locally)
            #              extra_args=['config_fc', '--fcompiler=gnu95'])
            #TODO install check silently failing
            #if not self.is_installed(environ, version, strict):
            #    raise Exception('SpacePy installation failed.')
