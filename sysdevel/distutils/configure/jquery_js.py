
import os
from sysdevel.distutils.fetching import fetch
from sysdevel.distutils.configuration import file_config, latest_version
from sysdevel.distutils import options

class configuration(file_config):
    """
    Fetch jQuery
    """
    def __init__(self):
        file_config.__init__(self, 'jquery.min.js',
                             os.path.join(options.target_build_dir,
                                          options.javascript_dir),
                             'http://code.jquery.com/', debug=False)


    def download(self, environ, version, strict=False):
        file_pattern = 'jquery-*.min.js'
        if version is None:
            version = latest_version('jquery', self.website, file_pattern)
        file_parts = file_pattern.split('*')
        js_file = file_parts[0] + version + file_parts[1]
        fetch(self.website, js_file, self.targets[0])
        return ''
