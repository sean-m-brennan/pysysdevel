
from ..fetching import fetch, unarchive
from ..configuration import py_config
from hdf5 import configuration as hdf5_lib

## Interdependency with hdf5 library is complex
class configuration(py_config):
    """
    Find/install h5py
    """
    def __init__(self):
        hdf5_ver, _, _, _ = hdf5_lib().get_version()
        if hdf5_ver is None:
            hdf5_ver = '1.8.4'
        version = '1.3.1'
        if hdf5_ver >= '1.8.4':
            version = '2.2.1'
        py_config.__init__(self, 'h5py', version,
                           dependencies=['hdf5 (>=' + hdf5_ver  + ')', 'lzf'],
                           debug=False)
