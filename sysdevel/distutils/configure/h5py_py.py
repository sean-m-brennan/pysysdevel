
import sys

from ..prerequisites import compare_versions, install_pypkg
from ..configuration import py_config
from .. import options

class configuration(py_config):
    """
    Find/install H5py (HDF5 for python)
    """
    def __init__(self):
        py_config.__init__(self, 'h5py', '2.1.2',
                           dependencies=[('hdf5', '1.8.3'), 'lzf'],
                           debug=False)


    def is_installed(self, environ, version=None):
        options.set_debug(self.debug)
        try:
            import h5py
            ver = h5py.version.version
            if compare_versions(ver, version) == -1:
                return self.found
            self.found = True
        except ImportError:
            if self.debug:
                print(sys.exc_info()[1])
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            website = 'http://h5py.googlecode.com/files/'
            if version is None:
                version = self.version
            src_dir = 'h5py-' + str(version)
            archive = src_dir + '.tar.gz'
            install_pypkg(src_dir, website, archive, locally=locally)
            ## FIXME Doesn't find the hdf5 shared lib
            #if not self.is_installed(environ, version):
            #    raise Exception('h5py installation failed.')
