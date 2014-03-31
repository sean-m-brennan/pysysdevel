
import os
import shutil

from ..fetching import fetch
from ..configuration import file_config
from .. import options

class configuration(file_config):
    """
    Fetch jQuery UI
    """
    def __init__(self):
        file_config.__init__(self, 'jquery-ui.min.js',
                             os.path.join(options.target_build_dir,
                                          options.javascript_dir),
                             dependencies=['jquery'], debug=False)
        ## add mousewheel plugin by default
        self.targets = ['jquery-ui.min.js', 'jquery.mousewheel.js']


    def install(self, environ, version, strict=False, locally=True):
        if version is None:
            version = '1.8.23'
        js_dir = self.target_dir
        website = 'http://code.jquery.com/ui/' + version + '/'
        js_file = self.targets[0]
        if not os.path.exists(js_dir):
            os.makedirs(js_dir)
        if not os.path.exists(os.path.join(js_dir, js_file)):
            fetch(website, js_file, js_file)
            shutil.copy(os.path.join(options.download_dir, js_file), js_dir)

        website = 'https://raw.github.com/brandonaaron/jquery-mousewheel/master/'
        js_file = self.targets[1]
        if not os.path.exists(js_dir):
            os.makedirs(js_dir)
        if not os.path.exists(os.path.join(js_dir, js_file)):
            fetch(website, js_file, js_file)
            shutil.copy(os.path.join(options.download_dir, js_file), js_dir)
