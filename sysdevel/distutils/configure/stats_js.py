
import os
from sysdevel.distutils.configuration import file_config
from sysdevel.distutils import options

class configuration(file_config):
    """
    Fetch three.js stats tool
    """
    def __init__(self):
        website = 'https://github.com/mrdoob/stats.js/blob/master/build/'
        file_config.__init__(self, 'stats.min.js',
                             os.path.join(options.target_build_dir,
                                          options.javascript_dir),
                             website, debug=False)
