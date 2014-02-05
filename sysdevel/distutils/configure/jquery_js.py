
import os
import shutil

from ..fetching import fetch
from ..configuration import file_config, latest_version
from .. import options

class configuration(file_config):
    """
    Fetch jQuery
    """
    def __init__(self):
        file_config.__init__(self, debug=False)


    def install(self, environ, version, locally=True):
        file_pattern = 'jquery-*.min.js'
        website = 'http://code.jquery.com/'
        if version is None:
            version = latest_version('jquery', website, file_pattern)
        file_parts = file_pattern.split('*')
        js_file = file_parts[0] + version + file_parts[1]
        js_dir = os.path.join(options.target_build_dir, options.javascript_dir)
        js_target = 'jquery.min.js'
        if not os.path.exists(js_dir):
            os.makedirs(js_dir)
        if not os.path.exists(os.path.join(js_dir, js_target)):
            fetch(website, js_file, js_file)
            shutil.copy(os.path.join(options.download_dir, js_file),
                        os.path.join(js_dir, js_target))
