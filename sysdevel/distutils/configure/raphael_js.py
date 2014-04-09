
import os
from ..fetching import fetch
from ..configuration import file_config
from .. import options

class configuration(file_config):
    """
    Fetch raphael
    """
    def __init__(self):
        website = 'http://github.com/DmitryBaranovskiy/raphael/raw/master/'
        file_config.__init__(self, 'raphael-min.js',
                             os.path.join(options.target_build_dir,
                                          options.javascript_dir),
                             website, debug=False)
        self.targets = ['raphael.min.js']


    def download(self, environ, version, strict=False):
        fetch(self.website, self.source, self.targets[0])
        return ''
