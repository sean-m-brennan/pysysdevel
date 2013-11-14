
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
        file_config.__init__(self, dependencies=['jquery'], debug=False)


    def install(self, environ, version, locally=True):
        if version is None:
            version = '1.8.23'
        website = 'http://code.jquery.com/ui/' + version + '/'
        js_file = 'jquery-ui.min.js'
        js_dir = os.path.join(options.target_build_dir, options.javascript_dir)
        if not os.path.exists(js_dir):
            os.makedirs(js_dir)
        if not os.path.exists(os.path.join(js_dir, js_file)):
            fetch(website, js_file, js_file)
            shutil.copy(os.path.join(options.download_dir, js_file), js_dir)
        ## add mousewheel plugin by default
        website = 'https://raw.github.com/brandonaaron/jquery-mousewheel/master/'
        js_file = 'jquery.mousewheel.js'
        if not os.path.exists(os.path.join(js_dir, js_file)):
            fetch(website, js_file, js_file)
            shutil.copy(os.path.join(options.download_dir, js_file), js_dir)
