
import os
import shutil

from sysdevel.util import *
from sysdevel.configuration import file_config

class configuration(file_config):
    """
    Fetch jQuery
    """
    def __init__(self):
        file_config.__init__(self, debug=False)


    def install(self, environ, version, locally=True):
        if version is None:
            version = '1.9.1'
        website = 'http://code.jquery.com/'
        js_file = 'jquery-' + version + '.min.js'
        js_dir = os.path.join(target_build_dir, javascript_dir)
        js_target = 'jquery.min.js'
        if not os.path.exists(js_dir):
            os.makedirs(js_dir)
        if not os.path.exists(os.path.join(js_dir, js_target)):
            fetch(website, js_file, js_file)
            shutil.copy(os.path.join(download_dir, js_file),
                        os.path.join(js_dir, js_target))
