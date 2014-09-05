
import os
from sysdevel.distutils.fetching import fetch
from sysdevel.distutils.configuration import file_config
from sysdevel.distutils import options

class configuration(file_config):
    """
    Fetch spin.js
    """
    def __init__(self):
        website = 'http://fgnass.github.io/spin.js/'
        file_config.__init__(self, 'spin.min.js',
                             os.path.join(options.target_build_dir,
                                          options.javascript_dir),
                             website, debug=False)


    def download(self, environ, version, strict=False):
        fetch(self.website, self.source, self.targets[0])
        return ''
