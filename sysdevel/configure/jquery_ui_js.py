
import os
import shutil

from sysdevel.util import *
from sysdevel.configuration import js_config

class configuration(js_config):
    """
    Fetch jQuery UI
    """
    def __init__(self):
        js_config.__init__(self, dependencies=['jquery'], debug=False)


    def install(self, environ, version, locally=True):
        if version is None:
            version = '1.8.23'
        website = 'http://code.jquery.com/ui/' + version + '/'
        js_file = 'jquery-ui.min.js'
        js_dir = os.path.join(target_build_dir, javascript_dir)
        if not os.path.exists(js_dir):
            os.makedirs(js_dir)
        if not os.path.exists(os.path.join(js_dir, js_file)):
            fetch(website, js_file, js_file)
            shutil.copy(os.path.join(download_dir, js_file), js_dir)
        ## add mousewheel plugin by default
        website = 'https://raw.github.com/brandonaaron/jquery-mousewheel/master/'
        js_file = 'jquery.mousewheel.js'
        if not os.path.exists(os.path.join(js_dir, js_file)):
            fetch(website, js_file, js_file)
            shutil.copy(os.path.join(download_dir, js_file), js_dir)
